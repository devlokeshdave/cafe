# Generated by Django 5.0 on 2024-07-28 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form_layouts', '0006_kot_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='kot',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
