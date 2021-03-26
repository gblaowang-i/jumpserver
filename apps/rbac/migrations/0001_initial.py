# Generated by Django 3.1 on 2021-03-26 07:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


def add_default_builtin_role(apps, schema_editor):
    auth_permissions_model = apps.get_model('auth', 'Permission')
    contenttypes_model = apps.get_model('contenttypes', 'ContentType')
    db_alias = schema_editor.connection.alias

    contenttypes_ids = list(
        contenttypes_model.objects.using(db_alias).filter(
            app_label='accounts', model__in=['account', 'safe']
        ).values_list('id', flat=True)
    )
    print('contenttype_ids: {}'.format(contenttypes_ids))

    auth_permissions = auth_permissions_model.objects.using(db_alias).filter(
        content_type__in=contenttypes_ids
    )
    print('auth_permissions: {}'.format(auth_permissions.values_list('codename', flat=True)))

    role_model = apps.get_model('rbac', 'Role')
    safe_admin_role_data = {
        'display_name': 'Safe Admin Role',
        'name': 'safe_admin',
        'type': 'safe',
        'is_builtin': True,
        'created_by': 'System',
        'comment': 'Safe Admin Role',
    }
    safe_admin_role = role_model.objects.using(db_alias).create(**safe_admin_role_data)
    safe_admin_role.permissions.set(auth_permissions)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_by', models.CharField(blank=True, max_length=32, null=True, verbose_name='Created by')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('display_name', models.CharField(max_length=256, verbose_name='Display name')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Name')),
                ('type', models.CharField(choices=[('safe', 'Safe')], default='safe', max_length=128, verbose_name='Type')),
                ('is_builtin', models.BooleanField(default=False, verbose_name='Built-in')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Comment')),
                ('permissions', models.ManyToManyField(blank=True, null=True, to='auth.Permission', verbose_name='Permission')),
            ],
        ),
        migrations.CreateModel(
            name='SafeRoleBinding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rbac.role', verbose_name='Role')),
                ('safe', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.safe', verbose_name='Safe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'unique_together': {('user', 'role', 'safe')},
            },
        ),
        migrations.RunPython(add_default_builtin_role),
    ]
