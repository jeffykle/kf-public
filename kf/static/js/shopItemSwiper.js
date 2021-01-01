
document.addEventListener('DOMContentLoaded', function() {

    var singleImage = numImages == 1        

    var mySwiper = new Swiper('#installation-carousel', {
        centeredSlides: !singleImage,
        slidesPerView: 'auto',
        spaceBetween: 50,
        speed: 1000,
        autoplay: {
            delay: 3000,
          },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev'
        },
        scrollbar: {
            el: '.swiper-scrollbar',
            draggable: true,
        },

      })
})