$(document).ready(function() {
    
    $('#images').on('change', function(e) {
        // Vider le conteneur de prévisualisation avant d'ajouter de nouvelles images
        $('#apercu-images').empty();

        // Récupérer la liste des fichiers sélectionnés
        const files = e.target.files;

        // Vérifier si des fichiers ont été sélectionnés
        if (files) {
            // Parcourir chaque fichier
            $.each(files, function(index, file) {
                // Créer un objet FileReader
                const reader = new FileReader();

                // Définir la fonction qui sera exécutée une fois la lecture terminée
                reader.onload = function(e) {
                    // Créer une balise <img> avec l'URL de données du fichier
                    const image = $('<img>').attr('src', e.target.result)
                    const parent = $('<p>').attr('class', 'apercu-image');
                    parent.append(image);
                    // Ajouter la balise <img> au conteneur de prévisualisation
                    $('#apercu-images').append(parent);
                };

                // Lire le fichier en tant qu'URL de données
                reader.readAsDataURL(file);
            });
        }
    });
});