document.addEventListener('DOMContentLoaded', function() {


    var button = document.querySelector('#braintree-submit-button');
    var submitDiv = document.querySelector('#braintree-submit-div');
    var submitForm = document.querySelector('#braintree-submit-form');

    var addAddressForm = $('#add-address-form')


    var recaptcha = document.querySelector('#g-recaptcha-response');

    if(recaptcha) {
        recaptcha.setAttribute("required", "required");
    }

    var select = $('#address-select')
    addAddressForm.on('submit', function(e) {
        e.preventDefault()
        const form = new FormData(e.target);
        const address = {}

        $('#address_components').children().each(function(i, e) {
            address[e.dataset.geo] = e.value
        })


        const url = "/shop/addaddress/"
        $.ajax({
            url: url,
            type: 'POST',
            headers: { "X-CSRFToken": csrf_token },
            data: {
                'address': JSON.stringify(address),
                'address2': form.get("address2")
                },
            dataType: 'json',
            success: function (data) {
                $('#address-select').empty();
                for (const obj in data.addresses) {
                    var option = $('<option></option>').attr("value", data.addresses[obj]['id']).text(data.addresses[obj]['address']);

                    if (data.addresses[obj]['selected']) { option.prop('selected', true)}
                    $('#address-select').append(option);
                }
                $('#id_address').val('');
                $('#address-select').prop( "disabled", true );
                $('#edit-address').collapse('show');
                $('#geo-address').collapse('hide');
                $('#geo-address-2').collapse('hide');
                $('#geo-address-submit').collapse('hide');
                $('#add-address-button').collapse('hide');

                bt()
                $('#dropin-loading').removeClass('d-none')
            }
        })
    })

    $('#address-select').change(function(e) {
        $('#address-select').prop( "disabled", true );
        $('#edit-address').collapse('show');
        $('#add-address-button').collapse('hide');
        $('#geo-address').collapse('hide');
        $('#geo-address-2').collapse('hide');
        $('#geo-address-submit').collapse('hide');
        $('#dropin-loading').removeClass('d-none')
        bt()
    })
    
    $('#edit-address').click(function() {
        $('#address-select').prop( "disabled", false );
        $('#add-address-button').collapse('show');
        $('#dropin-wrapper').addClass('d-none')
        dropinInstance.teardown()
    })


    var dropinInstance; //acessible outside of function

    function bt()  { 
        braintree.dropin.create({
        authorization: braintree_client_token,
        vaultManager: true,
        container: '#dropin-container',
        venmo: {},
        paypal: {
            flow: 'checkout',
            amount: order_total,
            currency: 'USD',
            buttonStyle: {
                color: 'black',
                shape: 'rect',
                size: 'medium'
            }
          },
        paypalCredit: {
            flow: 'checkout',
            amount: order_total,
            currency: 'USD',
            buttonStyle: {
                color: 'black',
                shape: 'rect',
                size: 'medium'
                }
            }
        }, function (clientErr, instance) {

            dropinInstance = instance; //available outside of function

            if (clientErr) {
            console.error('Error creating client.', clientErr);
            return;
            }
            $('#dropin-loading').addClass('d-none')
            $('#dropin-wrapper').removeClass('d-none')



            submitForm.addEventListener('submit', function (e) {

                e.preventDefault()

                $('#braintree-submit-button').addClass('d-none')

                $('#checkout-submit-loader').removeClass('d-none')


                instance.requestPaymentMethod(function (err, payload) {

                    var nonceInput = document.createElement("input")
                    nonceInput.setAttribute('name', 'paymentMethodNonce')
                    nonceInput.setAttribute('value', payload.nonce)
                    nonceInput.setAttribute('type', 'hidden')
                    submitForm.appendChild(nonceInput)

                    var addrInput = document.createElement("input")
                    addrInput.setAttribute('name', 'address')
                    addrInput.setAttribute('value', $('#address-select').val())
                    addrInput.setAttribute('type', 'hidden')
                    submitForm.appendChild(addrInput)

                    submitForm.submit()
                })

            });

            if (instance.isPaymentMethodRequestable()) {
              submitDiv.classList.remove('d-none')
              window.scrollBy(0, 250);
            }

            instance.on('paymentMethodRequestable', function (event) {
              submitDiv.classList.remove('d-none')
              window.scrollBy(0, 250);
            });

            instance.on('noPaymentMethodRequestable', function () {
              submitDiv.classList.add('d-none')
            });

        })
    }
    
})



