# Generated by Django 3.1 on 2020-09-11 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0013_auto_20200910_0752'),
    ]

    operations = [
        migrations.AddField(
            model_name='galleryitem',
            name='sale_disclaimer',
            field=models.CharField(blank=True, default='Shipping within the U.S. is included in the price.', max_length=250, null=True),
        ),
    ]
