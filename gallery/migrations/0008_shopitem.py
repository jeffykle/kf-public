# Generated by Django 3.1 on 2020-09-06 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0007_auto_20200905_1239'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopItem',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('gallery.galleryitem',),
        ),
    ]