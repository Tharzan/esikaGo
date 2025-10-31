$(function(){
    reservation = $('#form-2')
    blog = $('#info_head')
    bouton = $('#create-reservation')
    bouton.click(function(){
        blog.animate({
            opacity: 0 // Anime l'opacité à 0
          }, 1000, function() {
            $(this).hide();
            //reservation.show('size', { percent: 100 }, 3000);
            reservation.show('slide', { direction: 'up' }, 3000);
            //reservation.fadeIn(3000);
            //reservation.show('scale', { percent: 100 }, 2000);
              
            

          });
    })

    
});