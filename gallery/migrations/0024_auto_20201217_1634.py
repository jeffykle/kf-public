# Generated by Django 3.1 on 2020-12-17 22:34

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0023_auto_20201217_1330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installationpage',
            name='date',
            field=models.DateField(default=datetime.datetime(2020, 12, 17, 22, 34, 26, 669634, tzinfo=utc), verbose_name='Post date'),
        ),
    ]
