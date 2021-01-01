import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from gallery.models import (ExternalLink, Gallery, GalleryImage, GalleryItem,
                            InstallationMedium, InstallationPage)
from wagtail.images.models import Image


class Command(BaseCommand):
    def handle(self, *args, **options):
        ExternalLink.objects.all().delete()
        for item in GalleryItem.objects.all():
            item.direct_sale_price = Decimal(0.00)
            item.direct_sale = False
            item.stock = 0
            item.external_sale = False
            item.save()
        self.stdout.write(f"The shop has been emptied.")
