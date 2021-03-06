# Generated by Django 3.1 on 2020-09-11 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0014_galleryitem_sale_disclaimer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='galleryimage',
            name='caption',
            field=models.CharField(blank=True, help_text="Ex. 'Detail' or 'Installation view'", max_length=250, verbose_name='Image caption (optional)'),
        ),
    ]
