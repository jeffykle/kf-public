# open external links in a new window

from django.utils.html import escape
from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks
from wagtail.core.rich_text import LinkHandler
from wagtailorderable.modeladmin.mixins import OrderableMixin

from .models import HomePageImage


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

@hooks.register('construct_page_listing_buttons') 
def replace_page_listing_button_item(buttons, page, page_perms, is_parent=False, context=None):
    for index, button in enumerate(buttons):
       # basic code only - recommend you find a more robust way to confirm this is the add child page button
        if button.label == 'Delete' and page.__class__.__name__ == 'HomePageImage':
            button.label = 'Remove from home page'

    
class HomePageImagesButtonHelper(ButtonHelper):

    def get_buttons_for_obj(self, obj, exclude=['edit'], classnames_add=None, classnames_exclude=None):
        btns = super().get_buttons_for_obj(obj, exclude, classnames_add, classnames_exclude)
        return btns

class HomePageImageAdmin(OrderableMixin, ThumbnailMixin, ModelAdmin):
    model = HomePageImage
    menu_label = 'Edit the Home Page'  # ditch this to use verbose_name_plural from model
    menu_icon = 'edit'  # change as required
    menu_order = 1  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('admin_thumb', 'home_page_image', 'installation_page',)
    list_per_page = 50
    thumb_image_field_name = 'home_page_image'
    thumb_image_width = 150
    ordering = ['sort_order']
    button_helper_class = HomePageImagesButtonHelper



modeladmin_register(HomePageImageAdmin)
