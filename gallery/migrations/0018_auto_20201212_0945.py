# Generated by Django 3.1 on 2020-12-12 15:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0017_auto_20201212_0934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='galleryitem',
            name='direct_sale_type',
            field=models.ForeignKey(default='DirectSaleType.get_default_pk', null=True, on_delete=django.db.models.deletion.SET_NULL, to='gallery.directsaletype'),
        ),
    ]