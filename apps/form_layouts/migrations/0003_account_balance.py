# Generated by Django 5.0 on 2024-07-13 13:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_permission'),
        ('form_layouts', '0002_bill_regular'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account_balance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('complete', models.BooleanField()),
                ('bills', models.ManyToManyField(to='form_layouts.bill_regular')),
                ('cafe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.cafe')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form_layouts.regular_customer')),
            ],
        ),
    ]
