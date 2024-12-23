# Generated by Django 5.1.4 on 2024-12-21 14:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_accounts_max_duration_accounts_min_duration_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accounts',
            old_name='active',
            new_name='is_authenticated',
        ),
        migrations.AlterField(
            model_name='accounts',
            name='max_duration',
            field=models.PositiveIntegerField(default=60, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='accounts',
            name='min_duration',
            field=models.PositiveIntegerField(default=5, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(50)]),
        ),
    ]
