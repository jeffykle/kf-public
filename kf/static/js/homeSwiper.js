
document.addEventListener('DOMContentLoaded', function() {

    var singleImage = numImages == 1
    var slidesPerView = window.innerWidth <= 400 ? 1 : 'auto'
    var homeSwiper = new Swiper('#home-page-carousel', {
        centeredSlides: true,
        loop: !singleImage,
        slidesPerView: slidesPerView,
        spaceBetween: 10,
        grabCursor: true,
        speed: 1000,
        autoplay: {
            delay: 5000,
          },

        on: {
            resize: function() {
                setSlidesPerView(this)
            }
        }
    })


    function setSlidesPerView(sw) {
        sw.slidesPerView = window.innerWidth <= 400 ? 1 : 'auto' 
  }


})