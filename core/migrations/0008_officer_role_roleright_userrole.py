# Generated by Django 2.1.11 on 2019-10-25 12:00

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20191008_0923'),
    ]

    operations = [
        migrations.CreateModel(
            name='Officer',
            fields=[
                ('id', models.AutoField(db_column='OfficerID', primary_key=True, serialize=False)),
                ('uuid', models.CharField(db_column='OfficerUUID', default=uuid.uuid4, max_length=36, unique=True)),
                ('code', models.CharField(db_column='Code', max_length=8)),
                ('last_name', models.CharField(db_column='LastName', max_length=100)),
                ('other_names', models.CharField(db_column='OtherNames', max_length=100)),
            ],
            options={
                'db_table': 'tblOfficer',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(db_column='RoleID', primary_key=True, serialize=False)),
                ('uuid', models.CharField(db_column='RoleUUID', max_length=36)),
                ('name', models.CharField(db_column='RoleName', max_length=50)),
                ('altlanguage', models.CharField(blank=True, db_column='AltLanguage', max_length=50, null=True)),
                ('is_system', models.IntegerField(db_column='IsSystem')),
                ('is_blocked', models.BooleanField(db_column='IsBlocked')),
                ('validity_from', models.DateTimeField(db_column='ValidityFrom')),
                ('validity_to', models.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('audit_user_id', models.IntegerField(blank=True, db_column='AuditUserID', null=True)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
            ],
            options={
                'db_table': 'tblRole',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RoleRight',
            fields=[
                ('id', models.AutoField(db_column='RoleRightID', primary_key=True, serialize=False)),
                ('right_id', models.IntegerField(db_column='RightID')),
                ('validity_from', models.DateTimeField(db_column='ValidityFrom')),
                ('validity_to', models.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('audit_user_id', models.IntegerField(blank=True, db_column='AuditUserId', null=True)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
            ],
            options={
                'db_table': 'tblRoleRight',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(db_column='UserRoleID', primary_key=True, serialize=False)),
                ('validity_from', models.DateTimeField(db_column='ValidityFrom')),
                ('validity_to', models.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('audit_user_id', models.IntegerField(blank=True, db_column='AudituserID', null=True)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
            ],
            options={
                'db_table': 'tblUserRole',
                'managed': False,
            },
        ),
    ]
