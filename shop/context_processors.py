

from decimal import Decimal

from gallery.models import GalleryItem, InstallationPage


def stock_check(request):
    cart = request.session.get('cart', [])
    items = GalleryItem.objects.filter(pk__in=cart)
    errors = []
    total = Decimal(0.00)
    for item in items:
        if item.stock == 0 or item.direct_sale == False:
            request.session['cart'].remove(item.pk)
            request.session.modified = True
            errors.append(f'{item.title} is no longer in stock and was removed from your cart.') 
    for pk in cart:
        try:
            GalleryItem.objects.get(pk=pk)
        except GalleryItem.DoesNotExist:
            request.session['cart'].remove(pk)
            request.session.modified = True
            errors.append(f'Item with ID of {pk} could not be found in the database and was removed from your cart.')
    return {
        'errors': errors
    }

def current_installation(request):
    if 'installation' in request.GET:
        installation_id = request.GET.get('installation')
        installation = InstallationPage.objects.get(pk=installation_id)
        return {
            'installation': installation
        }
    else:
        return {
            'installation': None
        }
