# Generated by Django 3.1 on 2020-09-10 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0012_auto_20200909_1423'),
    ]

    operations = [
        migrations.RenameField(
            model_name='externallink',
            old_name='external_sale_url',
            new_name='url',
        ),
    ]
