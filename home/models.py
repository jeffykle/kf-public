from django.db import models
from gallery.models import GalleryImage, InstallationPage
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailorderable.models import Orderable


class HomePage(Page):

    headline = models.CharField(blank=True, max_length=250)
    slider_label = models.CharField(blank=True, null=True, default="Featured Works", max_length=60)
    body = RichTextField(blank=True, features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link', 'image', 'embed', 'code', 'superscript', 'subscript', 'strikethrough', 'blockquote'])
    footer = RichTextField(blank=True, features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link', 'image', 'embed', 'code', 'superscript', 'subscript', 'strikethrough', 'blockquote'])
    content_panels = Page.content_panels + [
        FieldPanel('headline', classname="title"),
        FieldPanel('body', classname="full"),
        FieldPanel('slider_label', classname="full", heading="Label for Featured Images"),
        FieldPanel('footer', classname="full"),
        InlinePanel('home_page_images', label="Featured Images"),

    ]
    # parent_page_types = []
    # subpage_types = []

class HomePageImage(Orderable):

    def default():
        return HomePage.objects.first()

    home_page_carousel = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='home_page_images', null=True, default=default)
    home_page_image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    
    def installation_page(self):
        gallery_image = GalleryImage.objects.filter(image=self.home_page_image).first()
        return gallery_image.item.get_parent()
    panels = [
        ImageChooserPanel('home_page_image'),
    ]
