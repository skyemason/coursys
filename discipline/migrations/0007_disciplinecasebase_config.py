# Generated by Django 2.2.28 on 2022-06-20 09:14

import courselib.json_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discipline', '0006_add_central_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='disciplinecasebase',
            name='config',
            field=courselib.json_fields.JSONField(default=dict),
        ),
    ]
