# Generated by Django 5.0 on 2024-07-03 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0003_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order_list',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('table', models.CharField(max_length=50)),
                ('date', models.DateField()),
                ('items', models.JSONField()),
                ('tax', models.FloatField()),
                ('discount', models.FloatField(blank=True, null=True)),
                ('total', models.FloatField()),
            ],
        ),
    ]
