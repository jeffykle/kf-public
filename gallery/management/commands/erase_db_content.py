from django.core.management.base import BaseCommand
from gallery.models import (ExternalLink, Gallery, GalleryImage, GalleryItem,
                            InstallationMedium, InstallationPage)
from home.models import HomePageImage
from wagtail.images.models import Image


class Command(BaseCommand):
    def handle(self, *args, **options):
        proceed = input('This command will delete all Pages and Images from the database. Are you sure you want to proceed? (Y/n)')
        if proceed == 'Y':
            ExternalLink.objects.all().delete()
            HomePageImage.objects.all().delete()
            GalleryImage.objects.all().delete()
            GalleryItem.objects.all().delete()
            InstallationPage.objects.all().delete()
            Image.objects.all().delete()

            self.stdout.write(f"Delete succesful.")
        else:
            self.stdout.write(f"Deletion was aborted.")
