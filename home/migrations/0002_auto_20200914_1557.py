# Generated by Django 3.1 on 2020-09-14 20:57

from django.db import migrations
import django.db.models.deletion
import home.models
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepageimage',
            name='home_page_carousel',
            field=modelcluster.fields.ParentalKey(default=home.models.HomePageImage.default, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='home_page_images', to='home.homepage'),
        ),
    ]