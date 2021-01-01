import json
from decimal import Decimal

import braintree
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import (Http404, HttpResponse, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from gallery.models import GalleryItem
from myforms.models import AddressForm
from slugify import slugify
from wagtailcache.cache import nocache_page

from .models import Cart, Order, UserAddress

if settings.BRAINTREE_PRODUCTION:
    braintree_env = braintree.Environment.Production
else:
    braintree_env = braintree.Environment.Sandbox
    print("Using Braintree sandbox environment.")


gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree_env,
        merchant_id=settings.BRAINTREE_MERCHANT_ID,
        public_key=settings.BRAINTREE_PUBLIC_KEY,
        private_key=settings.BRAINTREE_PRIVATE_KEY
    )
)


def email_preview(request, id):
    order = Order.objects.get(pk=id)
    return render(request, 'shop/order_confirmation.html', {'order': order})


@csrf_exempt
def additem(request):
    itemId = json.loads(request.POST['itemId'])
    cart = request.session.get('cart', [])
    if(itemId not in cart):
        try:
            cart.append(itemId)
            request.session['cart'] = cart
        except Exception:
            pass
    data = {'cart': request.session['cart']}
    print(request.session['cart'])
    return JsonResponse(data)


@csrf_exempt
def removeitem(request):
    itemId = json.loads(request.POST['itemId'])
    cart = request.session.get('cart', [])
    if(itemId in cart):
        try:
            cart.remove(itemId)
            request.session['cart'] = cart
        except Exception:
            pass
    data = {'cart': request.session['cart']}
    print(request.session['cart'])
    return JsonResponse(data)


@csrf_exempt
def removecartitem(request):
    itemId = json.loads(request.POST['itemId'])
    cart = request.session.get('cart', [])
    if(itemId in cart):
        try:
            cart.remove(itemId)
            request.session['cart'] = cart
            print('cart item removed')
        except Exception:
            print('exception found!!!!')
            pass
    items = GalleryItem.objects.filter(pk__in=request.session['cart'])
    total = Decimal(0.00)
    for item in items:
        total += item.direct_sale_price
    data = {'cart': request.session['cart'], 'total': total}
    return JsonResponse(data)


def recent_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-date')
    return render(request, 'shop/recent_orders.html', {'orders': orders})

@nocache_page
@login_required
def checkout(request):
    items = GalleryItem.objects.filter(pk__in=request.session['cart'])
    errors = []
    total = Decimal(0.00)
    for item in items:
        # Now done with context_processor
        # if item.stock == 0:
        #     request.session['cart'].remove(item.pk)
        #     request.session.modified = True
        #     errors.append(f'{item.title} ({item.direct_sale_price}) is no longer in stock and was removed from your cart.')
        # else:
        total += item.direct_sale_price
    items = GalleryItem.objects.filter(pk__in=request.session['cart'])

    if not request.session['cart']:
        return render(request, 'shop/cart.html', {'errors': errors})

    try:
        # Always fails, probably doesn't work with Checkout flow (vs. Vault with saved payment methods)
        braintree_client_token = gateway.client_token.generate(
            {"customer_id": request.user.id})
    except:
        braintree_client_token = gateway.client_token.generate({})

    context = {
        'braintree_client_token': braintree_client_token,
        'cart': items,
        'order_total': total,
        'address_form': AddressForm(),
        'errors': errors,
        'user_addresses': UserAddress.objects.filter(user=request.user, active=True)
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def payment(request):

    errors = []

    print(request.POST)
    items = request.session['cart']

    order = Order(
        status='processing',
        user=request.user,
        shipping_address=UserAddress.objects.get(pk=request.POST['address']),
        first_name=request.POST['first-name'],
        last_name=request.POST['last-name'],

    )
    order.save()  # Get an ID to add items

    form_total = Decimal(request.POST['order-total'])
    db_total = Decimal(0.00)
    for item in items:
        obj = GalleryItem.objects.get(pk=item)
        order.items.add(obj)
        db_total += obj.direct_sale_price
    print(db_total)
    print(form_total)

    # Braintree requires total to be displayed on checkout page.
    # Ensure the form value was not tampered with, or in case the
    # db price has changed, then throw an error .
    if db_total == form_total:
        order.total = db_total
        order.save()
    else:
        errors.append("The order amount was not authorized by the server.")
        return render(request, 'shop/cart.html', {'errors': errors})

    nonce_from_the_client = request.POST['paymentMethodNonce']

    result = gateway.transaction.sale({
        "amount": request.POST['order-total'],
        "payment_method_nonce": nonce_from_the_client,
        "options": {
            "submit_for_settlement": True
        }
    })

    if result.is_success:

        order.status = 'success'
        order.paypal_id = result.transaction.id
        order.save()
        for item in order.items.all():
            item.stock -= 1
            if item.stock == 0:
                item.direct_sale = False
            item.save()
        request.session['cart'] = []

        order_item_details = ""

        for item in order.items.all():
            order_item_details += f"""
    {item.title}
    {item.description}
    ${item.direct_sale_price}

"""
        html_context = {
            'base_url': settings.BASE_URL,
            'order': order,
            }
        html_message = render_to_string('shop/order_confirmation.html', html_context)
        try:
            send_mail(
                f'Order confirmation #{order.id} from Kayleigh Fichten Studio',
                f"""Thank you for placing your order with Kayleigh Fichten Studio!

Your Confirmation #: {order.id}

Order details:
{ order_item_details }

Total: ${order.total}
Date placed: {order.date}

Ship to:
{order.formatted_shipping_address}


--

{settings.BASE_URL}""",
                settings.DEFAULT_FROM_EMAIL,
                [order.user.email, 'get@jeffkelly.dev'],
                html_message = html_message,
                fail_silently=False,
            )
        except ConnectionResetError:
            print('failed to send email confirmation message')

        return redirect('shop:order-success', id=order.id)

    elif result.errors.deep_errors:
        return JsonResponse({'result': str(result.errors.deep_errors)})
    else:
        return JsonResponse({'result': {
            'code': result.transaction.processor_settlement_response_code,
            'text': result.transaction.processor_settlement_response_text
        }
        })


@nocache_page
def order_success(request, id):
    # try:
    order = Order.objects.get(pk=id)
    return render(request, 'shop/order_success.html', {'order': order})
    # except:
    # return render(request, 'shop/order_success.html', {'errors': ['This order could not be found.']})


@login_required
def addaddress(request):
    all_addresses = []
    result = json.loads(request.POST['address'])
    remapCols = {
        'raw': 'formatted_address', 'street_number': 'street_number', 'route': 'route', 'locality': 'locality',
        'postal_code': 'postal_code', 'state': 'administrative_area_level_1', 'state_code': 'administrative_area_level_1_short',
        'country': 'country', 'country_code': 'country_short', 'latitude': 'lat', 'longitude': 'lng'}
    address = {}
    for key, value in remapCols.items():
        address[key] = result[value]
    is_new = True
    address_formatted = address['raw'] + ', ' + request.POST['address2'] if len(
        request.POST['address2']) is not None else address['raw']

    for a in UserAddress.objects.filter(user=request.user):
        if a.formatted == address_formatted:
            all_addresses.append(
                {'address': a.formatted, 'id': a.id, 'selected': True})
            a.active = True
            a.save()
            is_new = False
        elif a.active == True:
            all_addresses.append(
                {'address': a.formatted, 'id': a.id, 'selected': False})
    if is_new:
        a = UserAddress(user=request.user, address=address,
                        address2=request.POST['address2'])
        a.save()
        all_addresses.append(
            {'address': a.formatted, 'id': a.id, 'selected': True})

    data = {'addresses': all_addresses}
    return JsonResponse(data)


@login_required
@csrf_exempt
def removeaddress(request):
    print(request.POST)
    adr_id = request.POST['id']
    adr = UserAddress.objects.get(pk=adr_id)
    adr.active = False
    adr.save()
    data = {'result': 'success', 'id': adr_id}
    return JsonResponse(data)
    # except Exception as e:
    #     data = {'result': 'failed', 'error': str(e)}
    #     return JsonResponse(data)


@nocache_page
def privacy_policy(request):
    return render(request, 'shop/privacy_policy.html')
