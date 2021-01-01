
document.addEventListener('DOMContentLoaded', function() {

    var singleImage = numImages == 1        

    var mySwiper = new Swiper('#installation-carousel', {
        centeredSlides: numImages < 3,
        watchOverflow: true,
        slidesPerView: 'auto',
        spaceBetween: 15,
        scrollbar: {
            el: '.swiper-scrollbar',
            draggable: true,
        },
        speed: 1000,
        autoplay: {
            delay: 5000,
          },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev'
        },
        keyboard: {
            enabled: true,
            onlyInViewport: false,
        },

      })

    mySwiper.slideTo(1,1000)
})