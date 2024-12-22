# Generated by Django 5.1.4 on 2024-12-21 07:01

import common.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='videofomats',
            old_name='nickname',
            new_name='format',
        ),
        migrations.RenameModel(
            old_name='Account',
            new_name='Accounts',
        ),
        migrations.CreateModel(
            name='AccountTokens',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_name', models.CharField(default=None, max_length=25, unique=True)),
                ('access_token', models.CharField(default=common.models.generate_token, max_length=50)),
                ('status', models.BooleanField(default=True)),
                ('createdTime', models.DateTimeField(auto_now_add=True)),
                ('updatedTime', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.accounts')),
            ],
            options={
                'unique_together': {('account', 'token_name')},
            },
        ),
    ]
