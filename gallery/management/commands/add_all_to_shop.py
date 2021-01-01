import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from gallery.models import (ExternalLink, Gallery, GalleryImage, GalleryItem,
                            InstallationMedium, InstallationPage)
from wagtail.images.models import Image


class Command(BaseCommand):
    def handle(self, *args, **options):
        chance = 0.2
        for item in GalleryItem.objects.all():
            d = random.random()
            e = random.random()
            if d < chance:
                item.direct_sale_price = Decimal(random.randint(10, 200))
                item.direct_sale = True
                item.stock = 1
                item.save()
            if e < chance:
                item.external_sale = True
                link = ExternalLink(
                    gallery_item=item,
                    description='Buy this print',
                    url='www.url.com',
                    )
                link.save()
                item.save()
        self.stdout.write(f"Some gallery items have been added to the shop.")
