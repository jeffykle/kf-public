import sys

from django.conf.urls import url
from django.contrib.admin.filters import SimpleListFilter
from django.db.models import Q
from django.templatetags.static import static
from django.urls import path, reverse
from django.utils.html import escape, format_html, format_html_join
from django_admin_parent_filter import ParentFilter
from shop.models import ShopItem
from wagtail.admin.menu import AdminOnlyMenuItem
from wagtail.admin.widgets import Button, PageListingButton
from wagtail.contrib.modeladmin.helpers import (AdminURLHelper, ButtonHelper,
                                                PageButtonHelper)
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks
from wagtail.core.models import Page
from wagtail.core.rich_text import LinkHandler
from wagtailcache.cache import clear_cache

from .models import GalleryItem, InstallationPage
from .views import UnpublishedChangesReportView


@hooks.register('after_create_page')
@hooks.register('after_edit_page')
def clear_wagtailcache(request, page):
    if page.live:
        clear_cache()
        
@hooks.register('register_reports_menu_item')
def register_unpublished_changes_report_menu_item():
    return AdminOnlyMenuItem("Pages with unpublished changes", reverse('unpublished_changes_report'), classnames='icon icon-star' + UnpublishedChangesReportView.header_icon, order=700)

@hooks.register('register_admin_urls')
def register_unpublished_changes_report_url():
    return [
        path('reports/unpublished-changes/', UnpublishedChangesReportView.as_view(), name='unpublished_changes_report'),
    ]

class NewWindowExternalLinkHandler(LinkHandler):
    # This specifies to do this override for external links only.
    # Other identifiers are available for other types of links.
    identifier = 'external'

    @classmethod
    def expand_db_attributes(cls, attrs):
        href = attrs["href"]
        # Let's add the target attr, and also rel="noopener" + noreferrer fallback.
        # See https://github.com/whatwg/html/issues/4078.
        return '<a href="%s" target="_blank" rel="noopener noreferrer">' % escape(href)


@hooks.register('register_rich_text_features')
def register_external_link(features):
    features.register_link_type(NewWindowExternalLinkHandler)


class ParentFilter(ParentFilter):
    """Wagtail admin Page parent filter"""
    title = None
    model = None
    parent_model = None
    count = False
    items = []
    depth = -1

    def get_children(self, parent):
        """return a list of children"""
        return parent.get_children().type(self.parent_model)

    @property
    def top_instance(self):
        """return top instance. model first_common_ancestor"""
        return Page.objects.type(self.model).first_common_ancestor()

    def get_postfix(self):
        """return postfix string (childs count)"""
        if self.count:
            count = self.model.objects.descendant_of(self.instance).count()
            return " (%s)" % count

    def lookups(self, request, model_admin):
        top = self.top_instance
        qs = self.items + self.child_lookups(self.top_instance)
        qs.sort(key=lambda x: x[1])
        return qs

    def queryset(self, request, queryset):
        """return queryset object"""
        if self.value() is None:
            return queryset
        parent = Page.objects.get(pk=self.value())
        return self.model.objects.descendant_of(parent).order_by('title')


@hooks.register('construct_page_listing_buttons')
def replace_page_listing_button_item(buttons, page, page_perms, is_parent=False, context=None):
    for index, button in enumerate(buttons):
        if button.label == 'Add child page':
            if page.__class__.__name__ == 'Shop':
                button.label = 'Add a listing to shop'
            if page.__class__.__name__ == 'Gallery':
                button.label = 'Add an installation to your gallery'
            if page.__class__.__name__ == 'InstallationPage':
                button.label = 'Add a piece to this installation'
        if button.label == 'Add series items':
            button.label == 'Add one or more items from you gallery'


class InstallationButtonHelper(ButtonHelper):

    # Define classes for our button, here we can set an icon for example
    view_button_classnames = ['button-small', 'icon', 'icon-list-ul']

    def view_button(self, obj):
        text = 'Manage these gallery items'
        return {
            # decide where the button links to
            'url': '/admin/gallery/galleryitem/?installation=' + str(obj.pk),
            'label': text,
            'classname': self.finalise_classname(self.view_button_classnames),
            'title': text,
        }

    add_button_classnames = ['button-small', 'icon', 'icon-plus']

    def add_gallery_item_button(self, obj):
        base_url = '/admin/pages/add/gallery/galleryitem/'
        next_url = '/?next=/admin/gallery/galleryitem/?installation='
        text = 'Add a gallery item to this installation page'
        return {
            # decide where the button links to
            'url': base_url + str(obj.pk) + next_url + str(obj.pk),
            'label': text,
            'classname': self.finalise_classname(self.add_button_classnames),
            'title': text,
        }

    def get_buttons_for_obj(self, obj, exclude=None, classnames_add=None,
                            classnames_exclude=None):
        btns = super().get_buttons_for_obj(
            obj, exclude, classnames_add, classnames_exclude)
        if 'view' not in (exclude or []):
            btns.append(
                self.view_button(obj)
            )
        # if 'create' not in (exclude or []):
        #     btns.append(
        #         self.add_gallery_item_button(obj)
        #     )
        return btns


class GalleryItemButtonHelper(ButtonHelper):

    # Define classes for our button, here we can set an icon for example
    edit_button_classnames = ['button-small', 'icon', 'icon-edit']
    exclude = ['edit_button']

    def edit_button(self, pk, classnames_add=None, classnames_exclude=None):
        base_url = '/admin/pages/' + str(pk) + '/edit'
        params = self.request.GET
        if 'installation' in params:
            installation_pk = self.request.GET['installation']
            next_url = '/?next=/admin/gallery/galleryitem/?installation=' + str(installation_pk)
        else:
            next_url = '/?next=' + self.request.path

        # Define a label for our button
        # {}'.format(self.verbose_name)
        text = 'Edit'
        return {
            # decide where the button links to
            'url': base_url + next_url,
            'label': text,
            'classname': self.finalise_classname(self.edit_button_classnames),
            'title': text,
        }


@hooks.register('insert_global_admin_js')
def global_admin_js():
    js_files = [
        'js/admin_edit.js',
    ]
    js_includes = format_html_join('\n', '<script src="{0}"></script>',
                                   ((static(filename),)
                                    for filename in js_files)
                                   )
    return js_includes


@hooks.register('after_publish_page')
def set_main_images(request, page):
    if page.__class__.__name__ == 'GalleryItem':
        print('This is a gallery item')
        for image in page.gallery_images.all():

            if image.set_as_main_shop_image:
                page.selected_main_shop_image = image
                image.set_as_main_shop_image = False
                image.save()
                new_revision = page.save_revision()
                if page.live:
                    new_revision.publish()

            if image.set_as_main_gallery_image:
                installation_page = page.get_parent().specific
                installation_page.selected_main_gallery_image = image
                image.set_as_main_gallery_image = False
                image.save()
                new_revision = installation_page.save_revision()
                if installation_page.live:
                    new_revision.publish()



class OnSaleFilter(SimpleListFilter):
    title = 'On Sale'
    parameter_name = 'on_sale'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(Q(direct_sale=True) | Q(external_sale=True))
        elif value == 'No':
            return queryset.filter(Q(direct_sale=False) and Q(external_sale=False))
        return queryset


class InstallationFilter(ParentFilter):
    title = "Installation"
    parameter_name = "installation"
    model = GalleryItem
    parent_model = InstallationPage
    count = True


class InstallationPageAdmin(ThumbnailMixin, ModelAdmin):
    model = InstallationPage
    # ditch this to use verbose_name_plural from model
    menu_label = 'Installations'
    menu_icon = 'view'  # change as required
    menu_order = 2  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    # or True to exclude pages of this type from Wagtail's explorer view
    exclude_from_explorer = False
    list_display = ('title', 'admin_thumb', 'medium', 'date',)
    list_filter = ('mediums',)
    list_per_page = 20
    search_fields = ('title', 'description')
    thumb_image_field_name = 'main_image'
    thumb_image_width = 100
    ordering = ('-date', 'title',)

    def medium(self, obj):
        return [m for m in obj.mediums.all()]
    # def date(self, obj):
    #     return obj.date
    button_helper_class = InstallationButtonHelper


class GalleryItemAdmin(ThumbnailMixin, ModelAdmin):
    model = GalleryItem
    # ditch this to use verbose_name_plural from model
    menu_label = 'Gallery Items'
    menu_icon = 'image'  # change as required
    menu_order = 3  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    # or True to exclude pages of this type from Wagtail's explorer view
    exclude_from_explorer = False
    list_display = ('title', 'admin_thumb', 'description',
                    'direct_sale', 'external_sale')
    list_filter = (OnSaleFilter, InstallationFilter,)
    list_per_page = 20
    search_fields = ('title', 'description')
    thumb_image_field_name = 'main_image'
    thumb_image_width = 100
    ordering = ('-last_published_at', 'title')
    button_helper_class = GalleryItemButtonHelper
    inspect_view_enabled = True


class ShopItemAdmin(ThumbnailMixin, ModelAdmin):
    model = ShopItem
    menu_label = 'Shop Items'  # ditch this to use verbose_name_plural from model
    menu_icon = 'pick'  # change as required
    menu_order = 4  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    # or True to exclude pages of this type from Wagtail's explorer view
    exclude_from_explorer = False
    list_display = ('title', 'admin_thumb', 'direct_sale', 'direct_sale_price',
                    'stock', 'external_sale', 'external_links', 'last_published_at', 'first_published_at')

    list_filter = ('direct_sale',)
    search_fields = ('title', 'description')
    thumb_image_field_name = 'main_image'
    ordering = ('-last_published_at', '-first_published_at')
    # def date(self, obj):
    #     return obj.get_parent().specific().date

    def external_links(self, obj):
        return [l.url for l in obj.external_links.all()]

    def date(self, obj):
        return obj.get_parent().specific.date

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show people managed by the current user
        return qs.filter(Q(direct_sale=True) | Q(external_sale=True))



# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(InstallationPageAdmin)
modeladmin_register(GalleryItemAdmin)
modeladmin_register(ShopItemAdmin)
