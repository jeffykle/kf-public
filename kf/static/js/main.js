
document.addEventListener('DOMContentLoaded', function() {

$('.alert').alert()

$(function () {
    $('[data-toggle="popover"]').length && $('[data-toggle="popover"]').popover()
})

$('.popover-dismiss').length && $('.popover-dismiss').popover({
    trigger: 'focus'
})

var infinite = new Waypoint.Infinite({
      element: $('.infinite-container')[0],
      onBeforePageLoad: function () {
        $('.loader').removeClass('d-none')
      },
      onAfterPageLoad: function ($items) {
        $('.loader').addClass('d-none')
      }
    });


    var addItemForm = $('.add-item-form')
    var addItemButton = $('.add-item-button')
    var removeCartItem = $('.remove-cart-item')

    function toggleAddButton() {
        const btn = addItemButton
        const chkOut = $('#goto-checkout')
        if (btn[0].classList.contains('remove-item')) {
            btn.addClass('btn-dark').removeClass('btn-light').removeClass('remove-item')
            btn.text('Purchase This Item')
            btn.off('hover');
            chkOut.addClass('d-none')
        } else {
            btn.removeClass('btn-dark').addClass('btn-light').addClass('remove-item')
            btn.hover(function() {
                btn.removeClass('btn-light').addClass('btn-warning')
            }, function() {
                btn.removeClass('btn-warning').addClass('btn-light')
            });
            btn.text('Item in cart (Click to remove)')
            chkOut.removeClass('d-none')
        }
    }

    if ( cartItems.includes(pageId) ) {
        toggleAddButton()
        //<button type="submit" class="add-item-button card-link btn btn-dark " onsubmit="return false">Purchase This Item</button>
    }

    addItemForm.on('submit', function(e) {
        e.preventDefault()
        if (addItemButton[0].classList.contains('remove-item')) {
            const url = "/shop/removeitem/"

            $.ajax({
                url: url,
                type: 'POST',
                data: {
                    'itemId': pageId
                    },
                dataType: 'json',
                success: function (data) {
                    toggleAddButton()
                    if(data.cart.length === 0) {
                        $('.cart-nav').addClass('d-none')
                    } else {
                        $('.cart-nav-text').text(`Cart(${data.cart.length})`)
                    }
                }
            })
        } else {
            const url = "/shop/additem/"
            $.ajax({
                url: url,
                type: 'POST',
                data: {
                    'itemId': pageId
                    },
                dataType: 'json',
                success: function (data) {
                    toggleAddButton()
                    $('.cart-nav').removeClass('d-none')
                    $('.cart-nav-text').text(`Cart(${data.cart.length})`)
                }
            })
        }
    })

    removeCartItem.on('submit', function(e) {
        e.preventDefault()
            const url = "/shop/removecartitem/"
            const itemId = e.target.dataset.itemId

            $.ajax({
                url: url,
                type: 'POST',
                data: {
                    'itemId': itemId
                    },
                dataType: 'json',
                success: function (data) {
                    $(`.item-${itemId}`).remove()

                    if(data.cart.length === 0) {
                        $('.cart-nav').addClass('d-none')
                        $('#cart-list').append("<a href='/shop' class='btn btn-link'>Your cart is empty. Click here to return to the shop.</a>")
                        $('#checkout-button-div').remove()
                        $('#checkout-total-div').remove()
                    } else {
                        $('#cart-total').text(`$${data.total}`)
                        $('.cart-nav-text').text(`Cart(${data.cart.length})`)
                    }
                }
            })

    })

    $('.remove-address').each(function(index, el) {
        $(this).on("click", function(event) {
            $.ajax({
                url: "/shop/removeaddress/",
                type: 'POST',
                data: {
                    'id': $(el).data('id')
                    },
                dataType: 'json',
                success: function (data) {
                    if (data.result === 'success') {
                        $(`#address-container-${data.id}`).remove()
                    }
                }
            })
        });        
    });



});

