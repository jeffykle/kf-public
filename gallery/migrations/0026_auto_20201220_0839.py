
# Generated by Django 3.1 on 2020-12-20 14:39

import datetime
from django.db import migrations, models
from django.utils.timezone import utc

import google.auth
from google.cloud import secretmanager as sm


def createsuperuser(apps, schema_editor):

    # Retrieve secret from Secret Manager 
    _, project = google.auth.default()
    client = sm.SecretManagerServiceClient()
    name = f"projects/{project}/secrets/admin_password/versions/latest"
    admin_password = client.access_secret_version(name=name).payload.data.decode("UTF-8")

    # Create a new user using acquired password
    from django.contrib.auth.models import User
    User.objects.create_superuser("admin", password=admin_password)

class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0025_auto_20201219_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installationpage',
            name='date',
            field=models.DateField(default=datetime.datetime(2020, 12, 20, 14, 39, 35, 633331, tzinfo=utc), verbose_name='Post date'),
        ),
        migrations.RunPython(createsuperuser),
    ]
