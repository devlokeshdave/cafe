# Generated by Django 5.0 on 2024-08-25 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form_layouts', '0007_kot_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='kot',
            name='active',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
