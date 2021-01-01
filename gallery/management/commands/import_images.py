import json
import os
import random
from datetime import datetime, timedelta
from io import BytesIO

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand, CommandError
from gallery.models import (Gallery, GalleryImage, GalleryItem,
                            InstallationMedium, InstallationPage)
from home.models import HomePageImage
from slugify import slugify
from wagtail.images.models import Image


class Command(BaseCommand):
    help = 'Importing pages and image content, for initial migration.'

    def handle(self, *args, **options):
        assigned_mediums = {'7 deadly sins': 'Collage', 'attempt to mimic water': 'Sculpture', 'bound': 'Collage', 'collage 2019': 'Collage', 'collage 2020': 'Collage', 'commissions': 'Mixed Media', 'containment': 'Mixed Media', 'dissimulation': 'Sculpture', 'dusk': 'Mixed Media', 'emily owens as a rock': 'Sculpture', 'endless nightmare': 'Painting', 'ephemeral embedding': 'Sculpture', 'exit landscape': 'Painting', 'fertile ground': 'Mixed Media', 'growth': 'Painting', 'house plant with artificial shadow': 'Mixed Media', 'i dreamt of you': 'Painting', 'imagined landscapes and watersources': 'Painting', 'imitation of a chair': 'Video', 'inconspicuous growth': 'Painting', 'moss': 'Painting', 'new mexico': 'Painting', 'no place (utopic traces)': 'Painting', 'object in the environment': 'Photography', 'paintings 2013': 'Painting', 'paintings 2014': 'Painting', 'paintings in flux': 'Painting', 'process': 'Photography', 'push (traces)': 'Video', 'representing abstraction': 'Mixed Media', 'return to soil': 'Mixed Media', 'shore': 'Mixed Media', 'tarot series': 'Collage', 'the zodiac': 'Collage', 'twin peaks': 'Collage', 'utopia': 'Painting', 'voyage: an expedition into materiality': 'Mixed Media'}
        self.stdout.write("Trying to add mediums...")
        mediums = ['Collage', 'Painting',
                   'Photography', 'Mixed Media', 'Sculpture', 'Video']
        post_date = datetime.today() - timedelta(days=365)
        for m in mediums:
            existing_mediums = [
                i.name for i in InstallationMedium.objects.all()]
            if m in existing_mediums:
                self.stdout.write(f"{m} already exists as a medium.")
            else:
                medium = InstallationMedium(name=m)
                medium.save()
        wd = os.path.abspath(os.getcwd())
        print(wd)
        with open(os.path.join(wd, 'organized.json'), 'r') as f:
            data = json.load(f)  # ['data']
            for page in reversed(data):
                name = page['name']
                body = page.get('body', '')
                items = page['items']

                gallery = Gallery.objects.first()

                installation = InstallationPage(
                    title=name,
                    slug=slugify(name),
                    date=post_date,
                    body=json.dumps(
                        [{
                            'type': 'paragraph',
                            'value': body
                        }]) if len(body) else None,
                    mediums=[InstallationMedium.objects.get(name=assigned_mediums[name])]
                )
                self.stdout.write(f"Initialized page {name}")
                gallery.add_child(instance=installation)
                # installation.save_revision().publish()
                # saved_items = []
                image_counter = 0
                for item_data in items:
                    gallery_item = GalleryItem(
                        title=name,
                        slug=slugify(name) + str(image_counter),
                        description=item_data.get('description','')
                    )
                    gallery_images = []
                    for img_data in item_data['images']:
                        filename = img_data['filename']
                        path = os.path.join(os.path.join(
                            wd, 'migration_images'), filename)

                        with open(path, "rb") as imagefile:

                            image = Image(file=ImageFile(
                                BytesIO(imagefile.read()),
                                name=filename),
                                title=name + '-' + filename.rsplit('.', 1)[0])
                            image.save()
                            gallery_image = GalleryImage(
                                image=image,
                                caption=img_data['caption']
                            )
                            gallery_images.append(gallery_image)
                            gallery_item.gallery_images.add(gallery_image)

                    self.stdout.write(
                        f"    Saved image {filename} to database")

                    installation.add_child(instance=gallery_item)
                    image_counter += 1

                # installation.gallery_images=saved_items
                installation.save_revision().publish()

                self.stdout.write(f"        Attached images to {name}.")

                self.stdout.write(
                    f"Published page {name} with {str(len(items))} images.")
                post_date = post_date + timedelta(days=1)
        self.stdout.write('Finalizing homepage and publishing all page objects...')
        all_images = list(GalleryImage.objects.all())
        random_images = random.sample(all_images, 5)

        for img_obj in random_images:
            img = img_obj.image
            featured_img = HomePageImage(home_page_image=img)
            featured_img.save()
        for item in GalleryItem.objects.all():
            item.save_revision().publish()
        self.stdout.write('Done.')
