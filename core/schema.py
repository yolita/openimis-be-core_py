import json
import re
from datetime import datetime as py_datetime

import graphene
from core import ExtendedConnection
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import HttpRequest
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import ModuleConfiguration, Control, MutationLog

MAX_SMALLINT = 32767
MIN_SMALLINT = -32768


class SmallInt(graphene.Int):
    """
    This represents a small Integer, with values ranging from -32768 to +32767
    """

    @staticmethod
    def coerce_int(value):
        res = super().coerce_int(value)
        if MIN_SMALLINT <= res <= MAX_SMALLINT:
            return res
        else:
            return None

    serialize = coerce_int
    parse_value = coerce_int

    @staticmethod
    def parse_literal(ast):
        result = graphene.Int.parse_literal(ast)
        if result is not None and MIN_SMALLINT <= result <= MAX_SMALLINT:
            return result
        else:
            return None


MAX_TINYINT = 255
MIN_TINYINT = 0


class TinyInt(graphene.Int):
    """
    This represents a tiny Integer (8 bit), with values ranging from 0 to 255
    """

    @staticmethod
    def coerce_int(value):
        res = super().coerce_int(value)
        if MIN_TINYINT <= res <= MAX_TINYINT:
            return res
        else:
            return None

    serialize = coerce_int
    parse_value = coerce_int

    @staticmethod
    def parse_literal(ast):
        result = graphene.Int.parse_literal(ast)
        if result is not None and MIN_TINYINT <= result <= MAX_TINYINT:
            return result
        else:
            return None


class OpenIMISJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, HttpRequest):
            if o.user:
                return f"HTTP_user: {o.user.id}"
            else:
                return None
        return super().default(o)


class OpenIMISMutation(graphene.relay.ClientIDMutation):
    class Meta:
        abstract = True

    internal_id = graphene.Field(graphene.String)

    class Input:
        client_mutation_label = graphene.String(max_length=255, required=False)

    @classmethod
    def async_mutate(cls, root, info, **data):
        pass

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        mutation_log = MutationLog.objects.create(
            json_content=json.dumps(data, cls=OpenIMISJSONEncoder),
            user_id=info.context.user.id if info.context.user else None,
            client_mutation_id=data.get('client_mutation_id'),
            client_mutation_label=data.get("client_mutation_label")
        )
        cls.async_mutate(root, info, **data)
        mutation_log.mark_as_successful()
        return cls(internal_id=mutation_log.id)


class ControlGQLType(DjangoObjectType):
    class Meta:
        model = Control


class ModuleConfigurationGQLType(DjangoObjectType):
    controls = graphene.List(ControlGQLType)

    def resolve_controls(parent, info):
        # TODO: find a way to prevent the N+1 query!
        return Control.objects.filter(field_name__startswith=parent.module + '.')

    class Meta:
        model = ModuleConfiguration


class MutationLogGQLType(DjangoObjectType):
    """
    This represents a requested mutation and its status.
    The "user" search filter is only available for super-users. Otherwise, the user is automatically set to the
    currently logged user.
    """
    class Meta:
        model = MutationLog
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "client_mutation_id": ["exact"],
            "client_mutation_label": ["exact"],
            "request_date_time": ["exact", "gte", "lte"],
            "status": ["exact", "gte"],
            "user": ["exact"],
        }
        connection_class = ExtendedConnection

    status = graphene.Field(graphene.Int,
                            description=", ".join([f"{pair[0]}: {pair[1]}" for pair in MutationLog.STATUS_CHOICES]))

    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_anonymous:
            return queryset.none()
        elif info.context.user.is_superuser:
            return queryset
        else:
            queryset = queryset.filter(user=info.context.user)
        return queryset


class Query(graphene.ObjectType):
    core_controls = graphene.List(
        ControlGQLType,
        module=graphene.String(required=True)
    )
    core_module_configurations = graphene.List(
        ModuleConfigurationGQLType,
        validity=graphene.String(),
        layer=graphene.String())

    mutation_logs = DjangoFilterConnectionField(MutationLogGQLType)

    def resolve_core_module_configurations(self, info, **kwargs):
        validity = kwargs.get('validity')
        # configuration is loaded before even the core module
        # the datetime is ALWAYS a Gregorian one
        # (whatever datetime is used in business modules)
        if validity is None:
            validity = py_datetime.now()
        else:
            d = re.split('\D', validity)
            validity = py_datetime(*[int('0' + x) for x in d][:6])
        # is_exposed indicates wherever a configuration
        # is safe to be accessible from api
        # DON'T EXPOSE (backend) configurations that contain credentials,...
        crits = (
            Q(is_disabled_until=None) | Q(is_disabled_until__lt=validity),
            Q(is_exposed=True)
        )
        layer = kwargs.get('layer')
        if layer is not None:
            crits = (*crits, Q(layer=layer))
        return ModuleConfiguration.objects.filter(*crits)

    def resolve_core_controls(self, info, **kwargs):
        return Control.objects.filter(
            field_name__startswith=kwargs.get('module') + "."
        )