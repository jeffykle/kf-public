# open external links in a new window

from django.utils.html import escape
from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks
from wagtail.core.rich_text import LinkHandler

from .models import Order


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

class OrderButtonHelper(ButtonHelper):

    # Define classes for our button, here we can set an icon for example
    edit_button_classnames = ['button-small', 'icon', 'icon-edit']
    exclude = ['edit', 'delete']

    def get_buttons_for_obj(self, obj, exclude=None, classnames_add=None,
                            classnames_exclude=None):
        if exclude is None:
            exclude = []
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        ph = self.permission_helper
        usr = self.request.user
        pk = getattr(obj, self.opts.pk.attname)
        btns = []
        if('inspect' not in exclude and ph.user_can_inspect_obj(usr, obj)):
            btns.append(
                self.inspect_button(pk, classnames_add, classnames_exclude)
            )
        if('edit' not in exclude and ph.user_can_edit_obj(usr, obj)):
            btns.append(
                self.edit_button(pk, classnames_add, classnames_exclude)
            )
        if('delete' not in exclude and ph.user_can_delete_obj(usr, obj)):
            btns.append(
                self.delete_button(pk, classnames_add, classnames_exclude)
            )
        return btns

@hooks.register('register_rich_text_features')
def register_external_link(features):
    features.register_link_type(NewWindowExternalLinkHandler)

class OrderAdmin(ThumbnailMixin, ModelAdmin):
    model = Order
    menu_label = 'Orders'  # ditch this to use verbose_name_plural from model
    menu_icon = 'list-ul'  # change as required
    menu_order = 10  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('user_username', 'user_email', 'date', 'status',)
    list_per_page = 50
    # search_fields = ('title', 'description')
    thumb_image_field_name = 'main_image'
    thumb_image_width = 100
    # ordering = ('date')
    inspect_view_enabled = True
    button_helper_class = OrderButtonHelper



modeladmin_register(OrderAdmin)
