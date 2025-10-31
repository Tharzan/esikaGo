

$(document).ready(function() 
{
    var page = $('#liste-page');
     var icon_page = $('#icon-page');
     icon_page.click(function(){
        page.toggle(1000);
        page.css('display','flex');
    });
    let scroll = $('.nav-scroll')
    menu = $('#menu_nav');
    var bouton = $('.line-icon');
    bouton.click(function(){
        
        menu.toggle(1000);
        
        scroll.css('display','none');

        

    });

    
    let lastScrollTop = 0; // Cette variable stocke la position de défilement précédente

// On ajoute un écouteur d'événement sur l'objet window pour détecter le défilement
window.addEventListener("scroll", function() {
    // On récupère la position de défilement actuelle
    let currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;

    // On compare la position actuelle à la précédente
    if (currentScrollTop > lastScrollTop) {
        // Défilement vers le bas
        scroll.css('display','none');
        
    } else {
        // Défilement vers le haut
        scroll.css('display','block');
    }

    // On met à jour la position de défilement pour la prochaine comparaison
    lastScrollTop = currentScrollTop <= 0 ? 0 : currentScrollTop;
}, false);
   





 
var blocks = $('.sroll-section')
blocks.addClass('defile');


$(window).on('scroll', function() {
 
 blocks.each(function(){
    var block = $(this)
 
 // Position du haut du bloc par rapport au haut du document
 var blockTop = block.offset().top;
 
 
 // Position actuelle de la fenêtre de défilement
 var windowTop = $(window).scrollTop();
 
 // Hauteur de la fenêtre du navigateur
 var windowHeight = $(window).height();

 // Condition pour déclencher l'animation
 // Le bloc est visible si le bas de la fenêtre de défilement est en dessous du haut du bloc
 // On ajoute un petit décalage (200px) pour qu'il s'anime avant d'être complètement visible
 if (windowTop + windowHeight > blockTop + 200) {
     // Ajoute la classe 'show' pour appliquer l'animation CSS
     block.addClass('show');

    
     
 }

 
});
});


var link = $('a.logout');
link.removeAttr('href');


link.click(function() {
    // Affiche l'overlay avec une animation de fondu
    
    
    // Affiche la boîte de dialogue avec une animation de fondu et d'agrandissement
    $(".dialog-box").css('z-index','200').animate({
        opacity: 1,
        scale: 1
    }, 400,function(){$(this).show(1000, function(){$(".overlay").fadeIn(100);});});
});


// Quand on clique sur le bouton "Annuler" ou l'overlay
$("#cancel-logout, .overlay").click(function() {
    // Cache la boîte de dialogue avec une animation de fondu
    $(".dialog-box").fadeOut(300, function() {
        // Réinitialise l'état initial après l'animation
        $(this).css({opacity: 0, scale: 0.8});
    });
    
    // Cache l'overlay
    $(".overlay").fadeOut(300);
});

// Quand on clique sur le bouton "Oui, me déconnecter"

//les icon


});