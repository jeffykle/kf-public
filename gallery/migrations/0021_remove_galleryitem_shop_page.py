# Generated by Django 3.1 on 2020-12-15 15:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0020_galleryitem_shop_page'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='galleryitem',
            name='shop_page',
        ),
    ]
