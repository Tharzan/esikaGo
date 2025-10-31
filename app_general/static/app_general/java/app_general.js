$(document).ready(function() 
{
   
   var block = $('.dossiers-section')
   block.addClass('defile');
   var block_2 = $('.community-section');
   block_2.addClass('defile');

   $(window).on('scroll', function() {
    
    
    
    // Position du haut du bloc par rapport au haut du document
    var blockTop = block.offset().top;
    var blockTop2 = block_2.offset().top;
    
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
    if (windowTop + windowHeight > blockTop2 + 200) {
        // Ajoute la classe 'show' pour appliquer l'animation CSS
        block_2.addClass('show');
        
    }
});

    const $grandDiv = $('#div-bloc-presentation');
    const $enfantDivs = $grandDiv.find('.bloc-presentation-mobile');
    let currentIndex = 0;
    const scrollDuration = 100; // Durée de l'animation de défilement en ms (1 seconde)
    let direction = 1;
    function scrollToNextDiv() {
        
        
        const targetScrollLeft = $grandDiv.width() * currentIndex;

        // Utilise .animate() de jQuery pour un défilement fluide
        $grandDiv.stop().animate({
            scrollLeft: targetScrollLeft
        }, scrollDuration, function() {
            // Cette fonction est appelée une fois l'animation terminée
            currentIndex+=direction;
            if (currentIndex >= $enfantDivs.length) {
                //direction *= -1; // Inverse la direction (1 devient -1, et -1 devient 1)
                //currentIndex += 2*direction;
                currentIndex=0;
                
            }
        });
    }

    // Démarre le défilement automatique toutes les 30 secondes
    setInterval(scrollToNextDiv, 10000); // 30000 millisecondes = 30 secondes

    // Défilement initial pour montrer la première div
   scrollToNextDiv();

});