

const video = document.getElementById('camera-feed');
        const canvas = document.getElementById('camera-canvas');
        const captureButton = document.getElementById('capture-btn');
        const photoInput = document.getElementById('photo-faciale-base64');
        const imagePreview = document.getElementById('captured-image-preview');
        let stream = null;

        /**
         * 1. Demande l'accès à la caméra et affiche le flux
         */
        async function startCamera() {
            try {
                // Demande l'accès aux flux vidéo (caméra)
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        facingMode: 'user' // Préfère la caméra frontale pour un selfie/reconnaissance
                    } 
                });
                video.srcObject = stream;
                video.play();
                console.log("Caméra démarrée.");

            } catch (error) {
                console.error("Erreur d'accès à la caméra : ", error);
                alert("Impossible d'accéder à la caméra. Vérifiez les permissions de votre navigateur.");
            }
        }

        /**
         * 2. Capture le cadre actuel et l'enregistre en Base64
         */
        captureButton.addEventListener('click', () => {
            if (!stream) {
                alert("Veuillez d'abord démarrer la caméra.");
                return;
            }

            // Assure que la taille du canvas correspond à la vidéo
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            // Dessine l'image de la vidéo sur le canvas
            canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Convertit le contenu du canvas en image Base64 (format JPEG)
            const imageDataURL = canvas.toDataURL('image/jpeg', 0.9);
            
            // Met à jour le champ caché du formulaire
            photoInput.value = imageDataURL;
            
            // Affiche l'aperçu et cache le flux vidéo (optionnel)
            imagePreview.src = imageDataURL;
            imagePreview.style.display = 'block';
            video.style.display = 'none';
            captureButton.textContent = 'Photo Capturée (Cliquez pour Recommencer)';
            
            // Optionnel: Arrêter le flux de la caméra après la capture pour économiser la batterie
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        });
        
        // Relancer la caméra si l'utilisateur veut recapturer
        video.addEventListener('click', () => {
            if (!stream) {
                video.style.display = 'block';
                imagePreview.style.display = 'none';
                startCamera();
                captureButton.textContent = 'Prendre la Photo';
            }
        });


        // Démarrer la caméra au chargement de la page
        //window.onload = startCamera;
    