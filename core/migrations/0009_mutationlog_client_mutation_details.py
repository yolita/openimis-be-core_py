# Generated by Django 2.1.14 on 2019-11-19 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_officer_role_roleright_userrole'),
    ]

    operations = [
        migrations.AddField(
            model_name='mutationlog',
            name='client_mutation_details',
            field=models.TextField(blank=True, null=True),
        ),
    ]