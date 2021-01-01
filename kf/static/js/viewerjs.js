document.addEventListener('DOMContentLoaded', function() {

    var getElementPosition = function(idClass) {
        var element = $(idClass);
        var offset = element.offset();
        return {
            'top': offset.top,
            'right': offset.left + element.outerWidth(),
            'bottom': offset.top + element.outerHeight(),
            'left': offset.left,
        };
    };


    const gallery = $('#installation-slides').length && new Viewer($('#installation-slides')[0], {
        title: function(img) {
            const url = new URL(img.src)
            const orig = document.querySelector('img[data-srcfull="'+url.pathname+'"]')
            const caption = orig.dataset.caption
            return caption
            },
        url(img) {
            return img.dataset.srcfull
        },
        toolbar: false,
        navbar: false,
    })

    $('#installation-slides').length && $('#installation-slides')[0].addEventListener('viewed', function(e) {
        $('.viewer-footer')[0].style.top = getElementPosition('.viewer-move').bottom + 10 + 'px'
    })

})