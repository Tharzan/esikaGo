from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from my_user.forms import *
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from blog.models import  Blog,BlogAdministrateur
from django.views.generic import UpdateView
from core.models import generer_cles_et_certificat,process_and_save_signature
from django.conf import settings

from django.contrib import messages
from pathlib import Path
from django.core.files import File
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from django.http import StreamingHttpResponse , HttpResponseNotFound
import os
import time 

from django.core.files.base import ContentFile

# Imports requis pour le traitement des fichiers et clés
import os
import uuid
import base64 

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, FileResponse, Http404
from django.core.files import File
from django.core.files.base import ContentFile
from pathlib import Path
import json


import tempfile
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers, PdfSignatureMetadata
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography import x509

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os 
from reportlab.lib.pagesizes import landscape


import base64
import tempfile
from cryptography.hazmat.backends import default_backend

import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from datetime import datetime
import uuid
import qrcode
import hashlib
import os
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch



from django.conf import settings

from hedera import Client, Status, TransactionId, TransactionRecord 


import tempfile
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers, PdfSignatureMetadata
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography import x509

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os 
from reportlab.lib.pagesizes import landscape


import base64
import tempfile
from cryptography.hazmat.backends import default_backend


import io 
import os 
import time
from django.shortcuts import redirect, render
from django.http import StreamingHttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.utils import timezone
from django.conf import settings # 🚨 NOUVEL IMPORT POUR ACCÉDER AUX PARAMÈTRES DJANGO
from reportlab.lib.pagesizes import A4
# ... (Autres imports reportlab) ...
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


from hedera import (
    Client, PrivateKey, AccountId, TopicId,
    TopicMessageSubmitTransaction, Status,
    # 🚨 Ajout de TransactionRecord pour obtenir l'horodatage
    TransactionRecord 
)

import uuid
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings
from dotenv import load_dotenv # Pour lire les variables d'environnement
from hedera import (
    Client, PrivateKey, AccountId, TopicId,
    TopicMessageSubmitTransaction, Status,
    TransactionRecord 
)

# Assurez-vous d'importer vos modèles, formulaires et utilitaires (pdf_utils)
from .models import DocumentSigne 
from .forms import DocumentUploadForm 
# Assurez-vous que ces fonctions sont disponibles




@login_required(login_url='login')
def security(request):
    
    user = request.user
    liste_blog = []
    
    try:
        administre = BlogAdministrateur.objects.filter(user=user)
        for objet in administre:
            liste_blog.append(objet.blog)
    except Exception as e:
         
        pass 
    
    # --- Traitement POST ---
    if request.method == 'POST':
        form = FormSecurity(request.POST, request.FILES) 
        password = request.POST.get('password')
        
        signature_file_object = request.FILES.get('signature') 
        base64_image_data = request.POST.get('verification_faciale')
        verification_faciale_file = None 
        
        

        
        if form.is_valid():
            # Gestion du cas 'profil_existe_deja' 
            if hasattr(request.user, 'security'):
                security = request.user.security
                security.delete() 
                
                
            # --- VÉRIFICATIONS MANUELLES et PRÉ-TRAITEMENTS ---
            
            if not signature_file_object:
                messages.error(request,'signature', "La photo de votre signature est manquante.")
                return render(request, 'MyUser/security.html', {'liste_blog': liste_blog})
            
            if not base64_image_data:
                messages.error(request,'verification_faciale', "La photo de vérification faciale est manquante.")
                return render(request, 'MyUser/security.html', {'liste_blog': liste_blog})
            
            # Décodage Base64
            try:
                if 'base64,' in base64_image_data:
                    format, imgstr = base64_image_data.split(';base64,') 
                    ext = format.split('/')[-1]
                else:
                    raise ValueError("Format Base64 invalide pour l'image faciale.")
                
                file_name = f'{user.username}_face_{uuid.uuid4()}.{ext}'
                verification_faciale_file = ContentFile(base64.b64decode(imgstr), name=file_name)
                
            except Exception as e:
                messages.error(request,'verification_faciale', f"Erreur lors du décodage de l'image faciale: {e}")
                return render(request, 'MyUser/security.html', { 'liste_blog': liste_blog})
            
            
            # --- 1. TRAITEMENT DE LA SIGNATURE (OpenCV) ---
            temp_path = None
            final_signature_abs_path = None
            
            try:
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
                os.makedirs(temp_dir, exist_ok=True)
                temp_filename = f"temp_{uuid.uuid4()}_{signature_file_object.name}"
                temp_path = os.path.join(temp_dir, temp_filename)
                
                with open(temp_path, 'wb+') as destination:
                    for chunk in signature_file_object.chunks():
                        destination.write(chunk)
                
                # final_signature_abs_path est le chemin ABSOLU du fichier traité
                final_signature_abs_path = process_and_save_signature(temp_path)
                
            except Exception as e:
                messages.error(request,'signature', f"Erreur lors du traitement de la signature : {e}")
                return render(request, 'MyUser/security.html', { 'liste_blog': liste_blog})
            
            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

            
            # --- 2. GÉNÉRATION DE CLÉS ---
            try:
                
                cle_privee_chemin, certificat_cle_publique = generer_cles_et_certificat(
                    request.user.username, 
                    password
                )
            except Exception as e:
                messages.error(request, f"Erreur de génération de clés : {e}")
                if final_signature_abs_path and os.path.exists(final_signature_abs_path):
                    os.remove(final_signature_abs_path)
                return render(request, 'MyUser/security.html', {'liste_blog': liste_blog})
            
            
            # --- 3. PRÉPARATION ET SAUVEGARDE FINALE DANS LA DB ---
            
            security_instance = form.save(commit=False)
            security_instance.user = request.user
            
            try:
                # Sauvegarde de la VÉRIFICATION FACIALE (ImageField)
                security_instance.verification_faciale.save(
                    verification_faciale_file.name, 
                    verification_faciale_file, 
                    save=False
                )
                
                # Sauvegarde de la SIGNATURE (ImageField)
                media_root_path = Path(settings.MEDIA_ROOT)
                final_path = Path(final_signature_abs_path) 
                signature_relative_path = final_path.relative_to(media_root_path).as_posix()
                
                with open(final_signature_abs_path, 'rb') as f:
                    file_object = File(f)
                    security_instance.signature.save(signature_relative_path, file_object, save=False)
                
                #  Sauvegarde de la CLÉ PUBLIQUE (FileField)
                certificat_path_obj = Path(certificat_cle_publique)
                certificat_relative_path = certificat_path_obj.relative_to(media_root_path).as_posix()
                
                with open(certificat_cle_publique, 'rb') as f_cert:
                    cert_file_object = File(f_cert)
                    security_instance.cle_publique.save(certificat_relative_path, cert_file_object, save=False)

            
                security_instance.save() 
                
                # Nettoyage de la signature traitée 
                if os.path.exists(final_signature_abs_path):
                    os.remove(final_signature_abs_path) 

                # Préparation de la redirection pour le téléchargement de la clé PRIVÉE
                request.session['cle_privee_a_telecharger'] = cle_privee_chemin
                request.session['certificat_a_supprimer'] = certificat_cle_publique # Sera supprimé par la vue suivante
                
                return redirect('succes_security_rl')
                
                
            except Exception as e:
                
                return render(request, 'MyUser/security.html', {'form': form, 'liste_blog': liste_blog})
            
        else:
            return render(request, 'MyUser/security.html', {'form': form, 'liste_blog': liste_blog})

    # --- Traitement GET ---
    else:
        form = FormSecurity()
        return render(request, 'MyUser/security.html', {
            'form': form, 
            'liste_blog': liste_blog,
            'revenu_user': True ,

        })


def document_view(request):
    user = request.user
    liste_blog = []
    if hasattr(request.user, 'security'): 
            has_security = True
    else:
            has_security = False
    
    try:
        administre = BlogAdministrateur.objects.filter(user=user)
        for objet in administre:
            liste_blog.append(objet.blog)
    except Exception as e:
        
        pass 
    return render(request, 'MyUser/document.html', {'liste_blog': liste_blog,'has_security': has_security  })


@login_required(login_url='login')
def succes_security_view(request):

    show_download_button = 'cle_privee_a_telecharger' in request.session
    
    context = {
        'show_download_button': show_download_button,
    }
    
    return render(request, 'MyUser/succes_security.html', context)


@login_required(login_url='login')
def download_security_files(request):
    
    cle_privee_path = request.session.get('cle_privee_a_telecharger')
    certificat_path = request.session.get('certificat_a_supprimer')
    
    # 1. Nettoyage immédiat de la session
    # Empêche le re-téléchargement si l'utilisateur clique plusieurs fois.
    if 'cle_privee_a_telecharger' in request.session:
        del request.session['cle_privee_a_telecharger']
    if 'certificat_a_supprimer' in request.session:

    
        if certificat_path and os.path.exists(certificat_path):
            os.remove(certificat_path)
        
    if not cle_privee_path or not os.path.exists(cle_privee_path):
        
        return HttpResponseNotFound("Le fichier de clé est introuvable ou a déjà été téléchargé.") 
        
    def file_iterator(file_path):
        """Lit le fichier par morceaux et le supprime APRES la lecture complète."""
        f = None
        try:
            f = open(file_path, 'rb')
            
            # Streaming du fichier
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk
        finally:
            
            if f:
                f.close() 
                
            time.sleep(0.5) 
            
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"INFO: Clé privée SUPPRIMÉE via StreamingHttpResponse: {file_path}")
            except Exception as e:
                print(f"ALERTE MAJEURE: Erreur de suppression de la clé: {e}")

    
    try:
        response = StreamingHttpResponse(
            file_iterator(cle_privee_path), 
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(cle_privee_path)}"'
        response['Content-Length'] = os.path.getsize(cle_privee_path)
        
        return response 
        
    except Exception as e:
        
        print(f"ERREUR TÉLÉCHARGEMENT: {e}")
        if os.path.exists(cle_privee_path):
            os.remove(cle_privee_path)
        
        
        return redirect('succes_security_url')


def createUser(request):
    
    if request.method == 'POST':

        form = FormulaireConnexion(request.POST)
        
        if form.is_valid():
            nom = form.cleaned_data['username']
            numero = form.cleaned_data['numero_tel']
            password = form.cleaned_data['password']
            user = form.save()
            user.username = nom
            user.save()
            login(request,user)
            return redirect(reverse('profil_user',kwargs={'user': request.user.id}))
            
            
        else:
            
            return render(request, 'MyUser/createUser.html')
        
    else:
        form =FormulaireConnexion()
    return render(request, 'MyUser/createUser.html', locals())



@login_required(login_url='login')
def editerUser(request):
    profile_instance= {}
    try:
        id = request.user.id
        my_user = MyUser.objects.get(id=int(id))
        
    except:
        return redirect('accueil')
    try:
        profile = ProfileUser.objects.get(user=my_user)
        has_profile = True
        field_name = ['contact_telephone','email','date_naissance','commune','rue',
                      'numero_rue','description']
        
        for field in field_name:
            field_value = getattr(profile, field)     
            if field_value is None:
                field_value = ''
            profile_instance[field] = field_value
    except:
        
        has_profile = False
    
    if request.method == 'POST':
        form = FormProfilUser(request.POST, request.FILES)
        save = False
        if form.is_valid():
            if has_profile:
                profile.delete()

            profil_save = form.save(commit=False)
            profil_save.user =  my_user
            profil_save.save()
            images_poste = ImageProfil(user=my_user)
            for image in request.FILES.getlist('image'):
                if image:
                    images_poste.image=image
                    save = True
                    
            for video in request.FILES.getlist('video'):
                if video:
                    images_poste.video=video
                    save = True
            if save:
                    
                images_poste.save()
            return redirect(reverse('profil_user', kwargs={'user': request.user.id}))
            
            
                
        else:
            
            formError = True
            form = FormProfilUser
            return render(request,'MyUser/edite_profil_user.html',{'form':form, 'profile':profile_instance})

            
    else:
        form = FormProfilUser
        return render(request,'MyUser/edite_profil_user.html',{'form':form, 'profile':profile_instance})

    
def profil_user(request, user):
    if int(user) == request.user.id:
        user = request.user
        
        has_blog = False
        liste_blog = list()
       
        try:
            administre  = BlogAdministrateur.objects.filter(user=user)
            for objet in administre:
                liste_blog.append(objet.blog)
            has_blog = True
            

        except:
            has_blog = False

        try:
            profile = user.profile
            has_profile = True
        except:
            has_profile = False

        try:
            picture = user.image
            
            has_picture = True
        except:
            has_picture = False

        return render(request,'MyUser/profil_user.html', locals())
    else:
        try:
            user = MyUser.objects.get(id=int(user))
            
            return render(request,'MyUser/profil_user.html', locals())
                
        except:
            return redirect('accueil')

class UpdateProfile(UpdateView):
    template_name = 'MyUser/edite_profil_user.html'
    model = ProfileUser
    form_class = FormProfilUser
    success_url = reverse_lazy('profil_user')

def updateProfile(form,list_keys,object):
    for key in list_keys:
        valeur = form.get(key)
        if valeur:
            object  = valeur

    return object


@login_required(login_url='login')
def gestion(request):


        user = request.user
        
        liste_blog= list()
        has_blog = True
        try:
            administre  = BlogAdministrateur.objects.filter(user=user)
            for objet in administre:
                liste_blog.append(objet.blog)
                
            

        except:
            has_blog = False
        return render(request, 'MyUser/gestion_user.html', locals())

@login_required(login_url='login')
def revenus(request):
    user = request.user
    liste_blog= list()
    has_blog = True
    try:
        administre  = BlogAdministrateur.objects.filter(user=user)
        for objet in administre:
            liste_blog.append(objet.blog)
                
    except:
        has_blog = False

    if request.method == 'POST':
            form = FormRevenus(request.POST)
            
            if form.is_valid():
                
                instance = form.save(commit=False)
                instance.user = user
                instance.save()
                return redirect('gestion_user')
            else:
                return render(request,'MyUser/revenu.html', {'formError':True, 'liste_blog': liste_blog})
        

    return render(request,'MyUser/revenu.html', {'liste_blog': liste_blog,'revenu_user':True})
    
   
@login_required(login_url='login')
def depenses(request):

    user = request.user
    liste_blog= list()
    has_blog = True
    try:
        administre  = BlogAdministrateur.objects.filter(user=user)
        for objet in administre:
            liste_blog.append(objet.blog)
                
    except:
        has_blog = False
    

    if request.method == 'POST':
        form = FormDepenses(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = user
            instance.save()
            return redirect('gestion_user')
        else:
            return render(request,'MyUser/depenses.html', {'formError':True, 'liste_blog': liste_blog})
        

            
    return render(request,'MyUser/depenses.html', {'liste_blog': liste_blog})
    


@login_required(login_url='login')
def dettes(request):
    user = request.user
    liste_blog= list()
    has_blog = True
    try:
        administre  = BlogAdministrateur.objects.filter(user=user)
        for objet in administre:
            liste_blog.append(objet.blog)
                
    except:
        has_blog = False

    if request.method == 'POST':
            form = FormDettes(request.POST)
            
            if form.is_valid():
                
                instance = form.save(commit=False)
                instance.user = user
                instance.save()
                return redirect('gestion_user')
            else:
                return render(request,'MyUser/dettes.html', {'formError':True, 'liste_blog': liste_blog})
        

    return render(request,'MyUser/dettes.html', {'liste_blog': liste_blog,'revenu_user':True})



FONT_NAME = 'Times-Roman'
BOLD_FONT_NAME = 'Times-Bold'
OBLIQUE_FONT_NAME = 'Times-Oblique'

try:
    pdfmetrics.registerFont(TTFont('Georgia', os.path.join(settings.STATICFILES_DIRS[0], 'fonts/georgia.ttf')))
    pdfmetrics.registerFont(TTFont('Georgia-Bold', os.path.join(settings.STATICFILES_DIRS[0], 'fonts/georgiab.ttf')))
    pdfmetrics.registerFont(TTFont('Georgia-Italic', os.path.join(settings.STATICFILES_DIRS[0], 'fonts/georgiai.ttf')))
    
    FONT_NAME = 'Georgia'
    BOLD_FONT_NAME = 'Georgia-Bold'
    OBLIQUE_FONT_NAME = 'Georgia-Italic'
except Exception:
    pass 


def generate_qr_code(uuid_code):
    """Génère le QR code pour la vérification de l'URL et retourne un objet BytesIO."""
    # L'URL d'authentification demandée
    url = f"http://0.0.0.0:8000/authentify/{uuid_code}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    fill_color_rgb = "#00007D" 
    
    img = qr.make_image(fill_color=fill_color_rgb, back_color="white") # <-- Utilisation de la nouvelle couleur
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def calculate_sha256(file_path):
    """Calcule le hash SHA-256 d'un fichier."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
    
        for chunk in iter(lambda: f.read(4096), b''):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def creer_pkcs12_temp(private_key, certificate, password_bytes, friendly_name=b"signer"):
    """
    Crée un fichier PKCS#12 temporaire contenant la clé et le certificat.
    Retourne le chemin du fichier .p12 temporaire (à supprimer après usage).
    """
  
    p12_bytes = pkcs12.serialize_key_and_certificates(
        name=friendly_name,
        key=private_key,
        cert=certificate,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(password_bytes)
    )
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".p12")
    tf.write(p12_bytes)
    tf.flush()
    tf.close()
    return tf.name



# --- Fonction Principale de Signature ---

def create_certified_pdf(pdf_source_path, signataire_user, unique_code):
   

    """
    Crée la page de certification avec la signature, le QR code de l'UUID, 
    et fusionne le tout avec le PDF source.
    """
    date_signature = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # 1. Préparation des éléments dynamiques
    signataire_nom = f"{signataire_user.first_name} {signataire_user.last_name}" 
    
    
    try:
        signature_field = signataire_user.security.signature
        if signature_field:
            
    
            from PIL import Image # Importé ici ou en haut du fichier

            
            pil_image = Image.open(signature_field.path)
        
            if pil_image.mode in ('RGBA', 'P', 'CMYK'):
                pil_image = pil_image.convert('RGB') 

            signature_reader = ImageReader(pil_image)

        else:
            raise Exception("Champ de signature vide.")
            
    except Exception as e:
        print(f"Erreur lors de la récupération de la signature : {e}. Utilisation d'un placeholder.")
        raise ValueError("L'utilisateur n'a pas d'image de signature configurée ou erreur de lecture.")


    qr_code_buffer = generate_qr_code(unique_code)
    qr_reader = ImageReader(qr_code_buffer)


   
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height_page = A4 
    sig_width, sig_height = 120, 60 

    # Titre
    c.setFont(BOLD_FONT_NAME, 14)
    c.drawCentredString(width / 2, height_page - 120, "Certification de signature électronique EsikaGo")

    # QR code
    qr_size = 120
    qr_x, qr_y = 100, height_page - 300
    c.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size)

    # Signature de l'utilisateur
    sig_x = 250 
    sig_y = height_page - 245 + 10 
    c.drawImage(signature_reader, sig_x, sig_y, width=sig_width, height=sig_height)

    # Texte de certification (avec police Georgia)
    c.setFont(FONT_NAME, 10)
    c.drawString(250, height_page - 230, f"Plateforme : EsikaGo Authentify")
    c.drawString(250, height_page - 290, f"Signataire : {signataire_nom}") 
    c.drawString(250, height_page - 305, f"Date et heure : {date_signature}")
    c.drawString(250, height_page - 320, f"Lien de vérification : {unique_code}") # Utilisation du code UUID ici

    # Mention légale (Utilisation de Helvetica-Oblique)
    c.setFont("Helvetica-Oblique", 9) 
    c.drawString(100, 100, "Ce document est certifié électroniquement via EsikaGo Authentify.")
    c.drawString(100, 85, "L'empreinte cryptographique est ancrée sur Hedera Hashgraph.")
    c.drawString(100, 70, "Toute modification du contenu invalidera cette certification.")

    c.save()
    buffer.seek(0)
    
    # 3. Fusionner la page finale au PDF original (PyPDF2)
    reader = PdfReader(pdf_source_path)
    writer = PdfWriter()

    for page_pdf in reader.pages:
        writer.add_page(page_pdf)

    # Ajout de la page de certification
    extra_page = PdfReader(buffer).pages[0] 
    writer.add_page(extra_page)

    # Le PDF final est écrit dans un BytesIO pour le retour
    output_buffer = BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    
    return output_buffer







HEDERA_CLIENT_READY = False
try:
    

    HCS_TOPIC_ID = settings.HCS_TOPIC_ID 
    OPERATOR_ID = settings.OPERATOR_ID 
    OPERATOR_KEY = settings.OPERATOR_KEY 
    # Récupérer le réseau pour la construction du lien HashScan
    NETWORK = os.environ.get("NETWORK", "testnet") 

    # 2. Configuration du Client
    client = Client.forTestnet() if NETWORK == "testnet" else Client.forMainnet()
    client.setOperator(OPERATOR_ID, OPERATOR_KEY)
    HEDERA_CLIENT_READY = True


except Exception as e:
    print(f"❌ Erreur de configuration du client Hedera. L'ancrage ne fonctionnera pas : {e}")



@login_required
def sign_and_anchor_document(request):
    """
    Gère l'affichage du formulaire (GET) et le traitement de la signature et de l'ancrage (POST).
    """

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        
    
        password_str = request.POST.get('password')
        private_key_file = request.FILES.get('private_key')
        
        if form.is_valid():
            uploaded_file = request.FILES['document_file']
            type_document = form.cleaned_data['type_document']
            unique_code = str(uuid.uuid4())
            
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_pdfs')
            os.makedirs(temp_dir, exist_ok=True)
            temp_input_filename = f"{unique_code}_original.pdf"
            temp_input_path = os.path.join(temp_dir, temp_input_filename)
            temp_output_filename = f"{unique_code}_signed.pdf"
            temp_output_path = os.path.join(temp_dir, temp_output_filename)

            with open(temp_input_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
                    
            p12_path = None 
            try:
                certified_pdf_buffer = create_certified_pdf(
                    pdf_source_path=temp_input_path,
                    signataire_user=request.user,
                    unique_code=unique_code
                )
            except ValueError as e:
                
                os.remove(temp_input_path)
                return HttpResponse(f"Erreur lors de la création du PDF certifié: {e}", status=400)


            with open(temp_output_path, 'wb') as f:
                f.write(certified_pdf_buffer.getvalue())


            
            try:
                if not password_str or not private_key_file:
                    raise ValueError("Mot de passe ou clé privée manquant pour la signature cryptographique.")

                password_bytes = password_str.encode('utf-8')
                cert_path = request.user.security.cle_publique.path 
                
                
                private_key_file.seek(0) 
                private_key_content = private_key_file.read()
                cle_privee = serialization.load_pem_private_key(
                    private_key_content, 
                    password=password_bytes,
                    backend=default_backend()
                )
                
                # 2.2. Chargement du certificat PEM
                with open(cert_path, "rb") as cf:
                    certificat = x509.load_pem_x509_certificate(cf.read(), default_backend())

                # 2.3. Créer un PKCS#12 temporaire 
                p12_path = creer_pkcs12_temp(cle_privee, certificat, password_bytes)


                try:
                    signer = signers.SimpleSigner.load_pkcs12(p12_path, passphrase=password_bytes)
                except AttributeError:
                    signer = signers.SimpleSigner.load_pkcs12(p12_path, password=password_bytes)

            
                signed_buffer = io.BytesIO()
                meta = PdfSignatureMetadata(
                    field_name='Signature_Securisee', 
                    reason='Document certifié et signé numériquement',
                    location='Kinshasa, CD'
                )
                
                
                with open(temp_output_path, 'rb') as doc: 
                    writer = IncrementalPdfFileWriter(doc)
                    meta = PdfSignatureMetadata(
                        field_name='Signature_Securisee',
                        reason='Reçu signé numériquement',
                        location='Kinshasa, CD'
                    )
                    signed_buffer = signers.sign_pdf(writer, meta, signer=signer)
                    signed_pdf_data = signed_buffer.read() 

                
            

        
                with open(temp_output_path, 'wb') as f:
                    f.write(signed_pdf_data)


                    ###

                    

            except Exception as e:
                print(f"❌ Erreur critique lors de la signature cryptographique (PyHanko): {e}")
            
                if os.path.exists(temp_input_path): os.remove(temp_input_path)
                if os.path.exists(temp_output_path): os.remove(temp_output_path)
                return HttpResponse(f"Erreur de signature cryptographique: {e}", status=400)
            finally:
                
                if p12_path and os.path.exists(p12_path):
                    try:
                        os.remove(p12_path)
                    except Exception:
                        pass
            
            # ------------------------------------------------------------------
            # 3. HASH du document FINALEMENT signé
            # ------------------------------------------------------------------
            document_hash = calculate_sha256(temp_output_path)
            
             # 2. Création de l'objet DocumentSigne avec statut initial
            doc_signature = DocumentSigne(
                type_document=type_document,
                document_hash_sha256=document_hash,
                signataire=request.user,
                hedera_timestamp="PENDING", 
                hedera_transaction_id="PENDING",
                lien_verification_hedera=None,
                statut="SIGNÉ",
                code=unique_code 
            )
            
            

            doc_signature.document_signe.save(
                f"{unique_code}_signed.pdf", 
                ContentFile(signed_pdf_data), 
                save=False
            )
            doc_signature.save() 

            
            
            # 3. --- APPEL À HEDERA HCS POUR L'ANCRAGE ---
            
            hcs_success = False

            if HEDERA_CLIENT_READY:
                try:

                    payload = {
            "hash": document_hash,
            "signataire": doc_signature, 
                   "type de document":type_document,
                
                "signataire":request.user.username
        }

                    message_to_send = json.dumps(payload, ensure_ascii=False).encode('utf-8')
           
                
                    
                    transaction = (
                        TopicMessageSubmitTransaction()
                        .setTopicId(HCS_TOPIC_ID)
                        .setMessage(message_to_send)
                    )

                    tx_response = transaction.execute(client)
                    # Attendre le record pour obtenir l'horodatage de consensus
                    record = tx_response.getRecord(client) 
                    
                    if record.receipt.status == Status.SUCCESS:
                        consensus_time = record.consensusTimestamp.toString()
                        tx_id = tx_response.transactionId.toString()
                        
                        # Construction du lien HashScan
                        explorer_link = f"https://hashscan.io/{NETWORK}/transaction/{tx_id}"
                        
                        # 4. Mise à jour de l'objet si succès
                        doc_signature.hedera_timestamp = consensus_time
                        doc_signature.hedera_transaction_id = tx_id
                        doc_signature.lien_verification_hedera = explorer_link
                        doc_signature.statut = "SIGNÉ & ANCRÉ"
                        hcs_success = True
                        
                        # Sauvegarde des champs mis à jour uniquement
                        doc_signature.save(update_fields=['hedera_timestamp', 'hedera_transaction_id', 'lien_verification_hedera', 'statut'])
                        print(f"✅ Document ancré sur Hedera. Transaction ID: {tx_id}")
                        
                    else:
                        doc_signature.statut = "SIGNÉ (Échec Ancrage HCS)"
                        doc_signature.save(update_fields=['statut'])
                        print(f"❌ ÉCHEC HCS. Statut : {record.receipt.status.toString()}")
                        
                except Exception as e:
                    doc_signature.statut = "SIGNÉ (Erreur de connexion HCS)"
                    doc_signature.save(update_fields=['statut'])
                    print(f"❌ Exception lors de l'appel HCS: {e}")
            else:
                print("⚠️ L'ancrage HCS a été ignoré car le client Hedera n'est pas configuré.")


            # 5. Nettoyage et Redirection
            os.remove(temp_input_path)
            os.remove(temp_output_path)
            
            return redirect('document_detail', pk=doc_signature.pk) 

        else:
            return render(request, 'MyUser/doc.html', {'form': form})
            
    else: # request.method == 'GET'
        form = DocumentUploadForm()
        return render(request, 'MyUser/document.html', {'form': form})
    



from django.shortcuts import get_object_or_404, render
from .models import DocumentSigne 


def document_detail(request, pk):
    """Affiche les détails du document signé et son statut d'ancrage."""
    document = get_object_or_404(DocumentSigne, pk=pk)
    return render(request, 'MyUser/document_detail.html', {'document': document})


def authentify_document(request, code):
    """
    Vue appelée par le QR code pour vérifier l'authenticité d'un document.
    """
    try:
        document = DocumentSigne.objects.get(code=code) 
        
        return render(request, 'MyUser/authentify_page.html', {
            'document': document,
            'is_valid': True,
            'verification_code': code
        })
        
    except DocumentSigne.DoesNotExist:
        # Si aucun document n'est trouvé, signale une erreur
        return render(request, 'MyUser/authentify_page.html', {
            'is_valid': False,
            'verification_code': code
        })