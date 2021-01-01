from decimal import Decimal

from address.models import AddressField
from django import forms
from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from gallery.models import GalleryImage, GalleryItem, InstallationPage
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (FieldPanel, FieldRowPanel,
                                         InlinePanel, MultiFieldPanel,
                                         StreamFieldPanel)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page, PageManager
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet


class Shop(RoutablePageMixin, Page):

    # ajax_template = "shop/shop_item_ajax.html"
    # subpage_types = ['ShopItem']
    # parent_page_types = []

    def get_context(self, request):

        context = super().get_context(request)
        shop_items = GalleryItem.objects.filter(Q(direct_sale=True) | Q(
            external_sale=True)).live().order_by('-last_published_at')

        paginator = Paginator(shop_items, 12)
        page = request.GET.get('page')

        try:
            items = paginator.get_page(page)
        except PageNotAnInteger:
            items = paginator.get_page(1)
        context['shop_items'] = items  # shop_items for all items
        for item in items:
            print(item)
        return context

    # view method for subpaths of /shop/
    @route(r'^((?!cart/|profile/)[-\w]+)/$')
    def item_view(self, request, item_slug):

        # context = self.get_context(request)
        if item_slug == 'cart':
            pass
        try:
            item = get_object_or_404(GalleryItem, slug=item_slug)
        except Exception:
            item = None
        if item is None:
            pass
        # context["item"] = item
        return render(request, "shop/shop_item.html", {
            'item': item,
            'shop_title': self.title,
            'shop_page_title': item.title,
        })


class ShopItem(GalleryItem, RoutablePageMixin):
    class Meta:
        proxy = True

    # parent_page_types = ['Shop']


class Cart(Page):

    def get_context(self, request):
        context = super().get_context(request)
        user = request.user
        session = request.session
        if 'cart' not in session:
            session['cart'] = []

        context['cart_total'] = Decimal(0.00)
        for item_id in session['cart']:
            try:
                p = GalleryItem.objects.get(pk=item_id).direct_sale_price
                context['cart_total'] += p
            except GalleryItem.DoesNotExist:
                pass

        context['cart'] = GalleryItem.objects.filter(pk__in=session['cart'])
        return context


class Profile(Page):
    def get_context(self, request):
        context = super().get_context(request)
        context['addresses'] = UserAddress.objects.filter(
            user=request.user, active=True)
        return context

class Order(models.Model):

    STATUS_OPTIONS = (
        ('processing', 'In Process, payment not submitted.'),
        ('success', 'Order Completed Succesfully'),
        ('failed', 'Order Failed'),
    )
    status = models.CharField(max_length=100, choices=STATUS_OPTIONS)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, )

    items = models.ManyToManyField(GalleryItem,)

    date = models.DateTimeField()
    user_username = models.CharField(max_length=320, )
    user_email = models.CharField(max_length=320, )
    total = models.DecimalField(
        "Order Total, $", blank=True, null=True, max_digits=6, decimal_places=2,)
    shipping_address = models.ForeignKey(
        'UserAddress', null=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=60, null=True)
    last_name = models.CharField(max_length=60, null=True)
    paypal_id = models.CharField(max_length=100, null=True, blank=True)

    @property
    def main_image(self):
        try:
            img = self.items.first().specific.main_image
        except Exception:
            print('Main image not found.')
            img = None
        return img

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date = timezone.now()
        self.user_username = self.user.username
        self.user_email = self.user.email

        return super(Order, self).save(*args, **kwargs)

    @property
    def formatted_shipping_address(self):
        frmt = ""
        addr = self.shipping_address.address
        frmt += self.first_name + " " + self.last_name + "\n"
        frmt += addr.street_number + " " + addr.route + "\n"
        if len(self.shipping_address.address2):
            frmt += self.shipping_address.address2 + "\n"
        frmt += str(addr.locality).replace(", United States", "")
        return frmt

    @property
    def html_formatted_shipping_address(self):
        frmt = ""
        addr = self.shipping_address.address
        frmt += self.first_name + " " + self.last_name + "<br>"
        frmt += addr.street_number + " " + addr.route + "<br>"
        if len(self.shipping_address.address2):
            frmt += self.shipping_address.address2 + "<br>"
        frmt += str(addr.locality).replace(", United States", "")
        return frmt

    panels = [


        FieldRowPanel([
            FieldPanel('total'),
            FieldPanel('status'),
            FieldPanel('paypal_id')
        ]),


        FieldRowPanel([
            FieldPanel('first_name'),
            FieldPanel('last_name'),
        ]),
        FieldPanel('shipping_address'),

        FieldPanel('date'),
        FieldPanel('user_username'),
        FieldPanel('user_email'),
        FieldPanel('items'),
    ]


class UserAddress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="user_address")
    address = AddressField()
    address2 = models.CharField(max_length=60, null=True, blank=True)
    active = models.BooleanField(default=True)

    @property
    def formatted(self):
        if self.address2 is not None and len(self.address2) > 0:
            return self.address.raw + ', ' + self.address2
        return self.address.raw

    def __str__(self):
        return self.formatted
