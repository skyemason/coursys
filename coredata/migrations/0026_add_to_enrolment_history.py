# Generated by Django 3.2.14 on 2025-05-14 14:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coredata', '0025_update_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrolmenthistory',
            name='enrl_drp',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='enrolmenthistory',
            name='wait_add',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='enrolmenthistory',
            name='wait_drp',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
