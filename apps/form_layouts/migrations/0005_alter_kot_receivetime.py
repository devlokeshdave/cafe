# Generated by Django 5.0 on 2024-07-23 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form_layouts', '0004_kot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kot',
            name='receiveTime',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
