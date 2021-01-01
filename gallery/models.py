from django import forms
from django.core.exceptions import ValidationError
from django.core.paginator import PageNotAnInteger, Paginator
from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.edit_handlers import (FieldPanel, InlinePanel,
                                         MultiFieldPanel, StreamFieldPanel)
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtailcache.cache import WagtailCacheMixin

from .custom_panels import ReadOnlyPanel


@register_snippet
class InstallationMedium(models.Model):
    name = models.CharField(max_length=255)
    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'installation mediums'


@register_snippet
class DirectSaleType(models.Model):
    direct_sale_type = models.CharField(max_length=255)
    panels = [
        FieldPanel('direct_sale_type'),
    ]

    def __str__(self):
        return self.direct_sale_type

    class Meta:
        verbose_name_plural = 'sale types'

    @classmethod
    def get_default_pk(cls):
        sale_type, created = cls.objects.get_or_create(
            direct_sale_type='Original')
        return sale_type.pk


class Gallery(WagtailCacheMixin, Page):

    intro = RichTextField(
        blank=True, help_text="Text for the top of your gallery page. "
        "(Optional - recommended to leave empty for a more simplistic look.)")

    content_panels = Page.content_panels + \
        [FieldPanel('intro', classname="full")]

    # subpage_types = ['InstallationPage']
    # parent_page_types = []

    def get_context(self, request):
        context = super().get_context(request)
        filtered_medium = request.GET.get('medium', None)
        if filtered_medium:
            context['filtered'] = True
            mediums = InstallationMedium.objects.filter(name=filtered_medium)
            installations = InstallationPage.objects.child_of(
                self).order_by('-date').live().filter(mediums__in=mediums)
        else:
            mediums = InstallationMedium.objects.filter(
                installationpage__in=InstallationPage.objects.all()).distinct()
            installations = InstallationPage.objects.child_of(
                self).order_by('-date').live()
        paginator = Paginator(installations, 8)
        page = request.GET.get('page')
        try:
            pagin = paginator.get_page(page)
        except PageNotAnInteger:
            pagin = paginator.get_page(1)
        context['installations'] = pagin
        context['mediums'] = mediums
        return context


class InstallationPage(WagtailCacheMixin, Page):

    date = models.DateField("Post date", default=timezone.now)
    mediums = ParentalManyToManyField(
        'InstallationMedium',
        default='Painting',
        help_text='Add more options by going to "Snippets" '
        'in the left hand menu.')
    # subpage_types = ['GalleryItem']
    # parent_page_types = ['Gallery']
    use_gallery = models.BooleanField(
        "Use gallery images",
        default=True,
        help_text="Turn the sliding gallery on or off. "
        "If you turn it off you can add your images in a "
        "custom format in the body below.")
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('video', EmbedBlock())
    ], blank=True)
    selected_main_gallery_image = models.ForeignKey(
        'GalleryImage', null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def on_sale(self, obj):
        return obj.external_sale or obj.direct_sale

    @property
    def main_image(self):
        if self.selected_main_gallery_image:
            return self.selected_main_gallery_image.image
        if self.get_children().count():
            img = self.get_children().specific().first().gallery_images.first()
            if img:
                return img.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('mediums', widget=forms.CheckboxSelectMultiple),
        FieldPanel('date'),
        FieldPanel('use_gallery'),
        StreamFieldPanel('body'),
        # InlinePanel('gallery_items', label="Gallery items"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['gallery_items'] = self.get_children(
        ).live().type(GalleryItem).specific()
        return context


class GalleryItem(WagtailCacheMixin, Page):

    subpage_types = []
    description = models.CharField(blank=True, max_length=250)
    direct_sale = models.BooleanField(
        "Direct Sale",
        default=False,
        help_text="Check this box to list this item for "
        "sale directly on your website.")
    direct_sale_price = models.DecimalField(
        "Sale price, $",
        blank=True,
        null=True,
        max_digits=6,
        decimal_places=2,
        help_text="Add more info about this item for the store page only.")
    direct_sale_extra_description = models.CharField(
        "Addtional sale description (optional)",
        blank=True,
        max_length=250, )
    stock = models.IntegerField("Number in stock", blank=True, null=True,)
    external_sale = models.BooleanField(
        "External Sale",
        default=False,
        help_text="Check this box to add external sale links (ex. Society6).")
    sale_disclaimer = models.CharField(
        blank=True,
        null=True,
        max_length=250,
        default="Shipping within the U.S. is included in the price.")
    direct_sale_type = models.ForeignKey(
        'DirectSaleType',
        on_delete=models.SET_NULL,
        null=True,
        default=DirectSaleType.get_default_pk,
        help_text='What type of item are you selling? '
        'You can add more options in the Snippets menu.')
    # parent_page_types = ['InstallationPage']
    selected_main_shop_image = models.ForeignKey(
        'GalleryImage', null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def on_sale(self, obj):
        return obj.external_sale or obj.direct_sale

    @property
    def main_image(self):
        if self.selected_main_shop_image:
            return self.selected_main_shop_image.image
        img = self.gallery_images.first()
        if img:
            return img.image
        return None

    @property
    def mediums(self):
        return self.get_parent().specific.mediums

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('description'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('external_sale'),
        MultiFieldPanel([
            InlinePanel('external_links',
                        label="External links (ex. Society6)"),
        ], heading="Add external sale links"),
        FieldPanel('direct_sale'),
        MultiFieldPanel([
            FieldPanel('direct_sale_type'),
            FieldPanel('direct_sale_price'),
            FieldPanel('direct_sale_extra_description'),
            FieldPanel('stock'),
            FieldPanel('sale_disclaimer'),
        ], heading="Add to shop (direct sale)"),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

    def save(self, *args, **kwargs):
        if self.stock == 0:
            self.direct_sale = False

        return super(GalleryItem, self).save(*args, **kwargs)

    def clean(self):
        if self.direct_sale:
            if not self.stock:
                raise ValidationError(
                    "Please set this item's stock to one or "
                    "more to list this item for sale.")
            elif self.stock < 1:
                raise ValidationError(
                    "Please set this item's stock to one or "
                    "more to list this item for sale.")
            elif not self.direct_sale_price:
                raise ValidationError(
                    'Please set a price to list this item for sale.')
            elif self.direct_sale_price < 0.01:
                raise ValidationError(
                    'Please set a price to list this item for sale.')
        if self.external_sale and self.external_links.count() is None:
            raise ValidationError(
                'Please add a least one external link, '
                'or uncheck "External Sale".')


class GalleryImage(Orderable):

    item = ParentalKey(
        GalleryItem,
        on_delete=models.CASCADE,
        related_name='gallery_images')
    image = models.ForeignKey('wagtailimages.Image',
                              on_delete=models.CASCADE, related_name='+')
    caption = models.CharField(
        "Image caption (optional)",
        blank=True,
        max_length=250,
        help_text="Ex. 'Detail' or 'Installation view'")
    set_as_main_gallery_image = models.BooleanField(
        default=False, help_text='Make this the primary image for this item '
        '(as displayed in the gallery).')
    set_as_main_shop_image = models.BooleanField(
        default=False, help_text='Make this the primary image for this item '
        '(as displayed in the shop).')

    @property
    def display_caption(self):
        verbose_name="Caption as displayed"
        parent_title = self.item.specific.title
        parent_description = self.item.specific.description
        installation_title = self.item.get_parent().specific.title

        if len(self.caption) > 0:
            dc = self.caption
        elif str(parent_title) != str(installation_title):
            dc = parent_title
        else:
            dc = parent_description
        return dc

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
        ReadOnlyPanel('display_caption', heading="Caption as displayed", help_text='If left blank, the item description at the top of this page will be shown instead.'),
        FieldPanel('set_as_main_gallery_image'),
        FieldPanel('set_as_main_shop_image'),
    ]


class ExternalLink(Orderable):

    gallery_item = ParentalKey(
        GalleryItem,
        on_delete=models.CASCADE,
        related_name='external_links',
        help_text="Add details about the listing, ex. dimensions, framing.")
    description = models.CharField(blank=True, max_length=250)
    url = models.URLField(
        blank=True,
        help_text="Add an external sale link (ex. Society6 prints)")

    def clean(self):
        if self.description is None and self.url is not None:
            raise ValidationError(
                "Please add a description for each external URL "
                "(it will be displayed on the product page).")
        if self.description is not None and self.url is None:
            raise ValidationError(
                "Please make sure each external URL is filled in.")
        if self.description is None and self.url is None:
            raise ValidationError(
                "Please remove all external links which were left blank.")
