from django.db import models
import qrcode
import uuid
import os
from django.utils.text import slugify 

from PIL import Image , ExifTags 
from django.core.files.uploadedfile import InMemoryUploadedFile 
from io import BytesIO 
from django.core.files.base import ContentFile


import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509
from cryptography.x509.oid import NameOID
from django.conf import settings


# Dans un fichier utilitaire de votre application Django (par exemple, mon_app/image_utils.py)

import cv2
import numpy as np
import os
import uuid
from django.conf import settings

# Fichier: utils.py ou similaire
# Nécessite: os, uuid, datetime, serialization, hashes, rsa, x509, NameOID, settings, File, ContentFile

def generer_cles_et_certificat(nom_signataire, mot_de_passe):
    # ATTENTION : La clé privée doit être sauvegardée en dehors du dossier public ou gérée avec soin.
    # Ici, nous laissons temporairement dans MEDIA_ROOT/signature, mais c'est à revoir pour la PROD.
    SIGNATURE_DIR = os.path.join(settings.MEDIA_ROOT, "signature") 
    
    os.makedirs(SIGNATURE_DIR, exist_ok=True)
    
    base_name = str(uuid.uuid4())
    
    # FICHIERS: Cle Privée (Key) et Certificat (PEM - la clé publique)
    FICHIER_CLE_NAME = f"{base_name}.key"
    FICHIER_CERT_NAME = f"{base_name}.pem"
    
    FICHIER_CLE_PATH = os.path.join(SIGNATURE_DIR, FICHIER_CLE_NAME)
    FICHIER_CERT_PATH = os.path.join(SIGNATURE_DIR, FICHIER_CERT_NAME) # Chemin ABSOLU
    
    # 1. Générer la Clé Privée (logique inchangée)
    # ... (Génération de cle_privee)
    cle_privee = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # 2. Définir les détails du certificat (logique inchangée)
    # ... (Définition de sujet, emetteur et construction du certificat)
    sujet = emetteur = x509.Name([
         x509.NameAttribute(NameOID.COUNTRY_NAME, "CD"), x509.NameAttribute(NameOID.COMMON_NAME, nom_signataire),
    ])
    certificat = x509.CertificateBuilder().subject_name(
        sujet 
    ).issuer_name(
        emetteur
    ).public_key(
        cle_privee.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    ).sign(cle_privee, hashes.SHA256(), padding.PKCS1v15())

    # 4. Écrire la clé privée (avec chiffrement) (logique inchangée)
    with open(FICHIER_CLE_PATH, "wb") as f:
        f.write(cle_privee.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(mot_de_passe.encode('utf-8'))
        ))

    # 5. Écrire le certificat (la clé publique)
    with open(FICHIER_CERT_PATH, "wb") as f:
        f.write(certificat.public_bytes(serialization.Encoding.PEM))

    print(f"FICHIERS CLÉS GÉNÉRÉS : Clé privée: {FICHIER_CLE_PATH}, Certificat: {FICHIER_CERT_PATH}")
    #

    # RETOURNER le chemin ABSOLU du fichier du certificat public
    return FICHIER_CLE_PATH, FICHIER_CERT_PATH # <--- CORRIGÉ pour retourner le chemin complet

def process_and_save_signature(image_path: str) -> str:
    """
    Découpe une image, convertit la signature en noir sur un fond blanc pur,
    la redimensionne et la sauvegarde dans MEDIA_ROOT/signature/ avec un nom UUID.

    Args:
        image_path (str): Chemin d'accès complet à l'image source.

    Returns:
        str: Le chemin d'accès complet au fichier de signature traité sauvegardé.
    """
    
    # 1. Charger l'image
    image = cv2.imread(image_path)
    
    if image is None:
        raise FileNotFoundError(f"Erreur : Impossible de lire l'image depuis le chemin : {image_path}")

    # 2. Traitement d'image OpenCV 
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Seuil binaire inversé (traits noirs sur fond blanc)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        raise ValueError("Erreur : Aucun contour n'a été trouvé dans l'image (pas de signature détectée).")
        
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Définir le buffer (la marge)
    buffer = 20
    
    # S'assurer que le nouveau cadre reste dans les limites de l'image
    x_start = max(0, x - buffer)
    y_start = max(0, y - buffer)
    x_end = min(image.shape[1], x + w + buffer)
    y_end = min(image.shape[0], y + h + buffer)

    # Découper l'image binaire pour un fond blanc pur
    cropped_image_binary = thresh[y_start:y_end, x_start:x_end]

    # 4. Redimensionner l'image en conservant les proportions
    (h_cropped, w_cropped) = cropped_image_binary.shape[:2]
    new_width = 350
    aspect_ratio = new_width / float(w_cropped)
    new_height = int(h_cropped * aspect_ratio)

    
    if new_height > 100:
        new_height = 105
        
    final_image_resized = cv2.resize(cropped_image_binary, (new_width, new_height), interpolation=cv2.INTER_AREA)

    
    
    # Définir le répertoire de stockage
    SIGNATURE_DIR = os.path.join(settings.MEDIA_ROOT, "signature")
    os.makedirs(SIGNATURE_DIR, exist_ok=True)
    
    # Générer un nom de fichier unique basé sur UUID
    file_name = f"{uuid.uuid4()}.png" # Utilisation de PNG pour la qualité binaire
    
    # Chemin d'accès complet au nouveau fichier
    final_path = os.path.join(SIGNATURE_DIR, file_name)

    # Sauvegarder l'image finale
    
    cv2.imwrite(final_path, final_image_resized)
    
    # Retourner le chemin complet du fichier sauvegardé
    return final_path


def generer_cles_et_certificat2(nom_signataire, mot_de_passe):

    SIGNATURE_DIR = os.path.join(settings.MEDIA_ROOT, "signature")

    # Créer le répertoire s'il n'existe pas
    os.makedirs(SIGNATURE_DIR, exist_ok=True)
    
    # Générer un UUID pour un nom de fichier unique
    base_name = str(uuid.uuid4())
    
    # Définir les chemins complets des fichiers
    FICHIER_CLE_NAME = f"{base_name}.key"
    FICHIER_CERT_NAME = f"{base_name}.pem"
    
    FICHIER_CLE_PATH = os.path.join(SIGNATURE_DIR, FICHIER_CLE_NAME)
    FICHIER_CERT_PATH = os.path.join(SIGNATURE_DIR, FICHIER_CERT_NAME)
    # 1. Générer la Clé Privée
    cle_privee = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # 2. Définir les détails du certificat
    sujet = emetteur = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CD"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Kinshasa"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Plateforme de Reçus"),
        x509.NameAttribute(NameOID.COMMON_NAME, nom_signataire),
    ])
    
    # 3. Construire le certificat (valide 1 an)
    certificat = x509.CertificateBuilder().subject_name(
        sujet 
    ).issuer_name(
        emetteur
    ).public_key(
        cle_privee.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    ).sign(cle_privee, hashes.SHA256(), padding.PKCS1v15())

    # 4. Écrire la clé privée (avec chiffrement)
    with open(FICHIER_CLE_PATH, "wb") as f:
        f.write(cle_privee.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(mot_de_passe.encode('utf-8'))
        ))

    # 5. Écrire le certificat
    with open(FICHIER_CERT_PATH, "wb") as f:
        f.write(certificat.public_bytes(serialization.Encoding.PEM))

    return FICHIER_CLE_NAME, FICHIER_CERT_NAME






def upload_to_unique_uuid(instance, filename):
        ext = filename.split('.')[-1]
        filename_unique = f"{uuid.uuid4().hex[:8]}.{ext}"
        return os.path.join('video_presentation', filename_unique)
    


    

class BaseImage(models.Model):

    def upload_to_unique_uuid(self, filename):
        ext = filename.split('.')[-1]
        filename_unique = f"{uuid.uuid4().hex[:8]}.{ext}"
        return os.path.join(self.url, filename_unique)
    
    def save(self, *args, **kwargs):
        image_modifiee = False
        if self.pk: 
            original_instance = self.objects.get(pk=self.pk)
        
            if original_instance.image != self.image:
                image_modifiee = True
        else: 
            image_modifiee = True

        # Traiter l'image seulement si elle est nouvelle ou a été modifiée
        if image_modifiee and self.image:
            # Lire le contenu du fichier uploadé en mémoire
            # Cela permet de le manipuler avec PIL sans le sauvegarder d'abord sur disque
            uploaded_image_file = self.image.file # Ceci est l'objet UploadedFile
            uploaded_image_file.seek(0) # Assurez-vous que le curseur est au début
            img = Image.open(uploaded_image_file)
            try:
                # On cherche la balise EXIF qui contient l'information d'orientation
                for cle_exif in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[cle_exif] == 'Orientation':
                        orientation_tag_id = cle_exif
                        break
                
                exif_data = img._getexif() # Récupère toutes les données EXIF de l'image
                
                if exif_data is not None:
                    # On obtient la valeur d'orientation
                    orientation = exif_data.get(orientation_tag_id)
                    
                    # On applique la rotation appropriée en fonction de la valeur d'orientation
                    if orientation == 3:
                        img = img.rotate(180, expand=True) # Rotation de 180 degrés
                    elif orientation == 6:
                        img = img.rotate(270, expand=True) # Rotation de 90 degrés dans le sens inverse des aiguilles d'une montre
                    elif orientation == 8:
                        img = img.rotate(90, expand=True) # Rotation de 270 degrés dans le sens inverse des aiguilles d'une montre
                    
                    # Important : supprime les données EXIF d'orientation après correction.
                    # Cela évite des problèmes si l'image est à nouveau traitée plus tard.
                    if orientation_tag_id in exif_data:
                        del exif_data[orientation_tag_id] # Supprime la balise d'orientation pour éviter des traitements futurs incorrects

            except (AttributeError, KeyError, IndexError, TypeError):
                # Il est possible que l'image n'ait pas de données EXIF, ou que la balise d'orientation manque.
                # Dans ce cas, on ne fait rien et on continue.
                pass

    


            largeur_actuelle, hauteur_actuelle = img.size
            largeur_max_pixels = 500 # La largeur maximale souhaitée

            if largeur_actuelle > largeur_max_pixels:
    
                rapport = largeur_max_pixels / largeur_actuelle
                nouvelle_hauteur = int(hauteur_actuelle * rapport)

                img_redimensionnee = img.resize((largeur_max_pixels, nouvelle_hauteur), Image.LANCZOS)

                # --- Déterminer le format de sauvegarde et la qualité (optimisé) ---
                # Utilisons le nom original pour déduire l'extension et donc le format de sauvegarde
                # (sauf si c'est un format à problème comme BMP/TIFF)
                ext = os.path.splitext(self.image.name)[1].lower()
                format_sauvegarde = 'jpeg' # Par défaut pour le web
                qualite = 95 # Qualité par défaut

                if ext in ['.png']:
                    format_sauvegarde = 'png'
                elif ext in ['.webp']:
                    format_sauvegarde = 'webp'
                    # Convertir en RGB si l'image WebP est en RGBA et que le mode transparent n'est pas nécessaire
                    # ou si vous voulez être sûr du support par tous les navigateurs.
                    # Pour WebP, PIL gère généralement bien la transparence si le format d'origine la supporte.
                else: # Pour JPG, BMP, TIFF, ou tout autre format inconnu, on sauve en JPEG
                    # Pour JPEG, si l'image a un canal alpha (transparence), convertissez-la en RGB
                    # avant de la sauvegarder, sinon vous aurez un fond noir.
                    if img_redimensionnee.mode == 'RGBA':
                        img_redimensionnee = img_redimensionnee.convert('RGB')


                temp_buffer = BytesIO()
                # Sauvegarder l'image redimensionnée dans le buffer temporaire
                # On passe le 'format' explicitement
                if format_sauvegarde in ['jpeg', 'webp']:
                    img_redimensionnee.save(temp_buffer, format=format_sauvegarde, quality=qualite)
                else: # Pour PNG, ou autres où quality n'est pas le même paramètre
                    img_redimensionnee.save(temp_buffer, format=format_sauvegarde)

                temp_buffer.seek(0) # Remettre le curseur au début du buffer

                # Remplacer le fichier original par le fichier redimensionné en mémoire
                # La magie de ContentFile : il prend le contenu binaire et se comporte comme un fichier
                self.image.file = ContentFile(temp_buffer.read())
                # Et assurez-vous que le content_type est correct
                self.image.file.content_type = f'image/{format_sauvegarde}'
                # Le nom du fichier sera géré par upload_to_unique_uuid lors du super().save() final
                print(f"Image redimensionnée et prête pour la sauvegarde : {self.image.name}")
            else:
                print(f"Image {self.image.name} est déjà <= {largeur_max_pixels}px de large. Pas de redimensionnement nécessaire.")
                # Si pas de redimensionnement, on pourrait vouloir lire le fichier uploadé
                # et le réassigner juste pour s'assurer que c'est bien l'UploadedFile qui est traité
                uploaded_image_file.seek(0)
                self.image.file = ContentFile(uploaded_image_file.read())
                self.image.file.content_type = uploaded_image_file.content_type


        # Appeler la méthode save() originale UNE SEULE FOIS pour sauvegarder l'instance
        # et le fichier image (potentiellement modifié/redimensionné)
        # upload_to_unique_uuid sera appelé ici pour donner un nom unique.
        super().save(*args, **kwargs)

    

    class Meta:
        abstract = True


 
 


class Reservation_appointment(models.Model):
    description = models.CharField(max_length=500, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_appointement = models.DateTimeField()
    status = models.CharField(max_length=50)#attent , annuler, reporter,reussi
    approuver = models.CharField(max_length=50)
    create_by = models.CharField(max_length=50) #selft or auther
    qr_resevation = models.ImageField(upload_to='appointment/qr')
    message_confirmation = models.CharField(max_length=255, null=True, blank=True)
    mont_total = models.IntegerField(null=True, blank=True)# le montant total facultatif
    montant_requis = models.IntegerField(null=True, blank=True)# nombre d'heure pourune anulation
    """ Montant obligatoire pour confirmer la reservation """
    #to_user
    #to_blog
    #from_user
    #from_blog
    class Meta:
        abstract = True
