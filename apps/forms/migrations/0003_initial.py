# Generated by Django 5.0 on 2024-07-01 14:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0002_permission'),
        ('forms', '0002_delete_menu'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('price', models.FloatField()),
                ('cafe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.cafe')),
            ],
        ),
    ]
