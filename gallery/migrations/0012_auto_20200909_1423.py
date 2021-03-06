# Generated by Django 3.1 on 2020-09-09 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0052_pagelogentry'),
        ('wagtailredirects', '0006_redirect_increase_max_length'),
        ('wagtailforms', '0004_add_verbose_name_plural'),
        ('gallery', '0011_galleryitem_external_sale'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shop',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='ShopItem',
        ),
        migrations.AlterField(
            model_name='galleryitem',
            name='direct_sale',
            field=models.BooleanField(default=False, help_text='Check this box to list this item for sale directly on your website.', verbose_name='Direct Sale'),
        ),
        migrations.DeleteModel(
            name='Shop',
        ),
    ]
