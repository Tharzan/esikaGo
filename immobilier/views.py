from django.shortcuts import render,HttpResponse, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from immobilier.models import ImageMaisons
from immobilier.forms import *
from django.contrib import messages
from blog.models import BlogAdministrateur
import datetime

from immobilier.models import *

import os
import hashlib
from dotenv import load_dotenv
import time 
from django.shortcuts import render, get_object_or_404
import os.path
from num2words import num2words
import threading 
from django.conf import settings
from .models import Loyer
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

def listeMaison(request):
    liste = [1,2,2,2,2,2,2,2,2]
    return render(request, 'immobilier/listeMasons_.html', locals())

def detailMaison(request):
    liste = [1,2,2,2,2,2,2,2,2]
    return render(request, 'immobilier/detail_maison.html', locals())

#@login_required(login_url=reverse('login'))
def post_maison(request):

    if request.method == 'POST':
        form = FormulairePostMaison(request.POST, request.FILES)

        if form.is_valid():
            post = form.save()
            
            for image in request.FILES.getlist('images'):
                if image:
                    images_poste = ImageMaisons(post_maison=post, image=image)
                    images_poste.save()
                else:
                    pass
            return HttpResponse('bien fait')
        else:
            messages.error(request, 'pppp')
    
            return HttpResponse('no,nnnnnn')
    else:
        form = FormulairePostMaison()
    return render(request,'immobilier/post_maison.html', locals())


#@login_required(login_url=reverse('login'))
def bien_immobilier(request):
    liste_blog = []
    
    nbr_biens =0
    occuper =0
    libre = 0
    revenus = 0

    
    
    try:

        property_all = SaveProperty.objects.filter(user=request.user)
        field_name = ['id','nom_complet_occupant','adresse','tel_occupant','type_bien','montant','id_maison','statut']
         # Créer une liste de dictionnaires
        data_property = []
       
        for property_item in property_all:
            
            
            if property_item.statut == 'occupe':
                occuper = occuper + 1
                revenus = revenus + property_item.montant
            
            property_dict = {}
            # Boucle sur les champs du modèle de manière dynamique
            for field in field_name:
                
                field_value = getattr(property_item, field)
                
                if field_value is None:
                    field_value = ''
                    

                property_dict[field] = field_value
            

            data_property.append(property_dict)
        nbr_biens = len(data_property)
        libre = nbr_biens - occuper

       

    except:
        pass
    if request.session['has_page']:

        
        
        administre  = BlogAdministrateur.objects.filter(user=request.user)
        for objet in administre:
                liste_blog.append(objet.blog)

    return render(request,'immobilier/bien_immobilier.html', {'liste_biens': data_property,'liste_blog':liste_blog,
    'nbr_biens':nbr_biens,'occuper':occuper,'libre':libre,'revenus':revenus})

def save_property(request):
    if request.method == 'POST':
        form = FormSave_property(request.POST, request.FILES)

        if form .is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('bien_immobilier')
        else:
            return render(request,'immobilier/save_property.html', {'formError':True,'form':form})
   
           
    else:
        return render(request,'immobilier/save_property.html', locals())
    

@login_required
def historique_maison(request,id):
        annee_actuelle = datetime.date.today().year
        try:
            
            id = int(id)
            property = SaveProperty.objects.get(id=id)
            
            if property.user != request.user:
                return redirect('accueil')
            
        except:
            
            return redirect('accueil')

        
        services_map = {'id':'id',
            'montant': 'montant',
            'date_payement': 'date_payement',
            'mois': 'mois',
            'observation': 'observation',}
        mois_paiement ={"1":'Janvier','2':'Février','3':'Mars',
            '4':'Avril','5':'Mai','6':'Juin','7':'Juillet','8':'Août','9':'Séptembre',
            '10':'Octobre','11':'Novembre','12':'Décembre'}
        
        mois ={"1":'Janv','2':'Fév','3':'Mars','4':'Avr','5':'Mai','6':'Juin','7':'Juil','8':'Août','9':'Sép','10':'Oct','11':'Nov','12':'Déc'}
        form = FormLoyer()
        has_historique = False
        liste_payement = property.historique.filter( annee=annee_actuelle)

        annees_uniques_queryset = property.historique.all().values('annee').distinct().order_by('-annee')

        liste_annees = [item['annee'] for item in annees_uniques_queryset]
    
        historique = []
        if liste_payement:
            for payement in liste_payement:
                
                has_historique = True
                item_payement = {}
                for champ_modele, nom_lisible in services_map.items():
                    value = getattr(payement, champ_modele)
                    if champ_modele == 'id':
                        item_payement['recu'] = value
                    
                    if champ_modele == 'date_payement':
                        year = value.year
                        month = value.month
                        month = mois[str(month)]
                        day = value.day
                        value = str(day) + ' ' + str(month) + ' ' + str(year)
                    elif champ_modele == 'mois':
                        
                        value = mois_paiement[str(value)]
                        
                        
                    
                    item_payement[champ_modele] = value
                    
                item_payement['nom_locataire'] = property.nom_complet_occupant
                item_payement['adresse'] = property.adresse
                item_payement['type'] = property.type_bien
                item_payement['loyer'] = property.montant
                item_payement['annee'] = annee_actuelle
                item_payement['id'] = property.id
                
                value = property.date_entrer
                year = value.year
                month = value.month
                month = mois[str(month)]
                day = value.day
                value = str(day) + ' ' + str(month) + ' ' + str(year)
                item_payement['dateentrer']  = value
                historique.append(item_payement)
        else:
                try:
                    item_payement = {}
                    item_payement['nom_locataire'] = property.nom_complet_occupant
                    item_payement['id'] = property.id
                    item_payement['adresse'] = property.adresse
                    item_payement['type'] = property.type_bien
                    item_payement['loyer'] = property.montant
                    item_payement['annee'] = annee_actuelle
                    value = property.date_entrer
                    year = value.year
                    month = value.month
                    month = mois[str(month)]
                    day = value.day
                    value = str(day) + ' ' + str(month) + ' ' + str(year)
                    item_payement['dateentrer']  = value
                    historique.append(item_payement)
                except:
                    item_payement = {}
                    item_payement['id'] = property.id
                    item_payement['annee'] = annee_actuelle
                    item_payement['nom_locataire'] = '-'
                    item_payement['adresse'] = property.adresse
                    item_payement['type'] = property.type_bien
                    item_payement['loyer'] = property.montant
                    
                    
                    item_payement['dateentrer']  = '-'
                    historique.append(item_payement)
        
        
        if request.method == 'POST':
            form = FormLoyer(request.POST)
            
            if form.is_valid():
                
   
                nouveau_loyer = form.save(commit=False)
                nouveau_loyer.property = property
    
                paiement_existant = Loyer.objects.filter(
                    property=property,
                    mois=nouveau_loyer.mois,
                    annee=nouveau_loyer.annee
                ).exists() 

                if paiement_existant:
                    # Doublon trouvé ! On affiche le message d'erreur et on ne sauve pas.
                    messages.info(
                        request, 
                        f"Les paiements pour le mois {nouveau_loyer.mois} et l'année {nouveau_loyer.annee} existent déjà pour cette maison. Veuillez le modifier à la place."
                    )
                    
                    
                    return redirect(reverse( 'historique_maison', kwargs={'id': property.id}))
                
                # --- SAUVEGARDE SI AUCUN DOUBLON ---
                
                # Sauvegarde l'instance si le doublon n'existe pas
                name = f"{uuid.uuid4().hex[:16]}"
                data = 'http://172.20.10.3:8000/verify/' + name
                nouveau_loyer.image_qr(data)
                nouveau_loyer.code = name
                nouveau_loyer.save()
                
                
                return redirect(reverse( 'view_quittance', kwargs={'id': nouveau_loyer.id}))
                        
            
            else:

                return render(request,'immobilier/historique_maison.html',{'form': form,'liste_annees':liste_annees, 'formError':True,'payement':historique,'has_historique':has_historique})
        
        else:
            
            return render(request,'immobilier/historique_maison.html', {'liste_annees':liste_annees,'form': form,'payements':historique,'has_historique':has_historique})   




def convertir_nombre_en_texte_francais(nombre):
    
    try:
        # 'lang='fr'' essentiel pour obtenir la traduction en français.
        texte_resultat = num2words(nombre, lang='fr')
        return texte_resultat
    except:
        return "Erreur"
    


def update_consensus_timestamp(loyer_id, tx_id_str):
    """Exécute l'appel bloquant getRecord dans un thread séparé."""
    try:
        loyer = Loyer.objects.get(id=loyer_id)
        client = Client.forTestnet()
        
        # 1. Reconstruire l'ID de Transaction à partir de la chaîne stockée
        tx_id = TransactionId.fromString(tx_id_str)
        
        # 2. Exécuter l'opération LENTE (getRecord)
        # Ceci attend la confirmation finale, mais ne bloque pas le serveur web.
        record = TransactionRecord.newQuery().setTransactionId(tx_id).execute(client)
        
        # 3. Sauvegarder l'Horodatage si la transaction est un succès
        if record and record.receipt.status == Status.SUCCESS:
            # Le consensusTimestamp est un objet qu'il faut convertir en string
            loyer.tp_hedera = record.consensusTimestamp.toString() 
            loyer.save()
            print(f"✅ Horodatage mis à jour pour Loyer ID {loyer_id}: {loyer.tp_hedera}")
        
    except Exception as e:
        # En cas d'échec (ex: Testnet trop lent ou transaction jamais trouvée)
        print(f"❌ Échec de la récupération du Timestamp pour Loyer ID {loyer_id}: {e}")
def calculate_file_hash(request,file_path_on_disk): # Renommé l'argument pour la clarté
    hasher = hashlib.sha256()
    try:
        # Utiliser l'argument qui est maintenant garanti d'être un chemin
        with open(file_path_on_disk, 'rb') as file:
            buf = file.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except FileNotFoundError:
        # CORRECTION : Retourner un message d'erreur Django
        messages.error(request, f"Erreur: Le fichier '{file_path_on_disk}' n'a pas été trouvé.")
        return None
    
def ancre_hedera(request, loyer):

    
    document_file_path = loyer.url_document.path 

    HCS_TOPIC_ID = settings.HCS_TOPIC_ID 
    OPERATOR_ID = settings.OPERATOR_ID 
    OPERATOR_KEY = settings.OPERATOR_KEY 
    
    client = Client.forTestnet()
    client.setOperator(OPERATOR_ID, OPERATOR_KEY)

   
        
    document_hash = calculate_file_hash(request,document_file_path) 

    document_hash = calculate_file_hash(request,document_file_path) 
    
    mois_map = {"1":'Janvier','2':'Février','3':'Mars','4':'Avril','5':'Mai','6':'Juin','7':'Juillet','8':'Août','9':'Séptembre','10':'Octobre','11':'Novembre','12':'Décembre'}
        

    if document_hash:
        
        mois_annee_str = mois_map[str(loyer.mois)] + ' ' + str(loyer.annee)
        
        payload = {
            "hash": document_hash,
            "Locataire": loyer.property.nom_complet_occupant, 
            "description": 'Paiement du loyer ' + mois_annee_str,
         
            "bailleur": loyer.property.user.username 
        }

        message_to_send = json.dumps(payload, ensure_ascii=False).encode('utf-8')

        
        transaction = (
            TopicMessageSubmitTransaction()
            .setTopicId(HCS_TOPIC_ID)
            .setMessage(message_to_send)
        
            
        )
       

        try:

            tx_response = transaction.execute(client)
    
            record = tx_response.getRecord(client)
            
            if record.receipt.status == Status.SUCCESS:
                
                consensus_time = record.consensusTimestamp.toString()
                loyer.ancre_hedera = document_hash
                loyer.tp_hedera = consensus_time
                loyer.signer = True
                loyer.save() 
                

            

                return True 
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de l'envoi de la transaction Hedera : {e}")
            return False        
        

    return False # Retourne False si le hash n'a pas pu être calculé


def update_consensus_timestmp(loyer_id, tx_timestamp_for_link):
    """
    Exécute l'appel bloquant TransactionRecord.newQuery en arrière-plan.
    Met à jour le champ 'tp_hedera' avec le véritable Horodatage de Consensus.
    """
    try:
        loyer = Loyer.objects.get(id=loyer_id)
        
        # 1. Configurer le client
        client = Client.forTestnet()
        # OPERATOR_ID est nécessaire pour reconstruire le TxID complet
        client.setOperator(settings.OPERATOR_ID, settings.OPERATOR_KEY) 
        
        # 2. Reconstruire l'ID de Transaction complet (Ex: 0.0.X@1762263256.202613000)
        full_tx_id_str = f"{settings.OPERATOR_ID.toString()}@{tx_timestamp_for_link}" 
        tx_id = TransactionId.fromString(full_tx_id_str)
        
        # 3. Exécuter l'opération LENTE et bloquante
        record = TransactionRecord.newQuery().setTransactionId(tx_id).execute(client)
        
        if record and record.receipt.status == Status.SUCCESS:
            
            # 4. Stocker l'Horodatage de CONSENSUS (la preuve finale)
            # Ceci met à jour le champ tp_hedera dans la base de données après la latence du réseau
            loyer.tp_hedera = record.consensusTimestamp.toString() 
            loyer.save()
            print(f"✅ Horodatage de Consensus mis à jour pour Loyer ID {loyer_id}: {loyer.tp_hedera}")
        
    except Loyer.DoesNotExist:
        print(f"Loyer ID {loyer_id} non trouvé pour mise à jour.")
    except Exception as e:
        print(f"❌ Échec de la récupération du Record en arrière-plan pour Loyer ID {loyer_id}: {e}")




@login_required    
def view_quittance(request,id):
    
        quittance = Loyer.objects.get(id=int(id))
        if quittance.signer:
            quittance_signer = True
        else:
            quittance_signer = False

        property = quittance.property
        if hasattr(request.user, 'security'): 
            has_security = True
        else:
            has_security = False

        services_map = {
            'montant': 'montant',
            'date_payement': 'date_payement',
            'mois': 'mois','id':'id',
            'observation': 'observation',}
        mois ={"1":'Janvier','2':'Février','3':'Mars','4':'Avril','5':'Mai','6':'Juin','7':'Juillet','8':'Août','9':'Séptembre','10':'Octobre','11':'Novembre','12':'Décembre'}
        recus={}
        for champ_modele, nom_lisible in services_map.items():
            value = getattr(quittance, champ_modele)
                
            if champ_modele == 'date_payement':
                year = value.year
                month = value.month
                day = value.day
                recus['date'] = str(day) + '/' + str(month) + '/' + str(year)
                month = mois[str(month)]
                
                
                value = str(month) + ' ' + str(year)

                recus['concerne'] = value
                if month in ['Avril','Octobre','Août']:
                    value = "d'" + str(month).lower() + ' ' + str(year)
                else:
                    value = "de " + str(month).lower() + ' ' + str(year)

            recus[champ_modele] = value

                
            recus['nom_locataire'] = property.nom_complet_occupant
            recus['adresse'] = property.adresse
            recus['type'] = property.type_bien
            recus['bailleur'] = request.user.username
            #print(recus['montant'])
            #valeur = recus['montant']
            #valeur = float(valeur)
            montant = int(recus['montant'])

            montant_text = convertir_nombre_en_texte_francais(montant)
            recus['montant_text'] = montant_text

        return render(request,'immobilier/apercu_quittance.html', {'recus': recus,
     'has_security': has_security,'quittance_signer': quittance_signer})   

   


STATIC_ROOT = settings.BASE_DIR 
try:
    
    # Méthode plus robuste : construire le chemin complet de manière dynamique
    def get_font_path(font_filename):
       
        return os.path.join(settings.BASE_DIR, 'static', 'fonts', font_filename) 

    pdfmetrics.registerFont(TTFont('Georgia', get_font_path('georgia.ttf')))
    pdfmetrics.registerFont(TTFont('Georgia-Bold', get_font_path('georgiab.ttf')))
    pdfmetrics.registerFont(TTFont('Georgia-Italic', get_font_path('georgiai.ttf')))
    pdfmetrics.registerFont(TTFont('Georgia-BoldItalic', get_font_path('georgiaz.ttf')))
    
    FONT_NAME = 'Georgia'
    BOLD_FONT_NAME = 'Georgia-Bold'
    BOLD_OBLIQUE_FONT_NAME = 'Georgia-BoldItalic'

except Exception as e:
    # Fallback si les fichiers sont introuvables (y compris en production si collectstatic n'est pas fait)
    print(f"ALERTE POLICE: Impossible de charger Georgia. Erreur: {e}")
    FONT_NAME = 'Times-Roman'
    BOLD_FONT_NAME = 'Times-Bold'
    BOLD_OBLIQUE_FONT_NAME = 'Times-BoldItalic'

from deepface import DeepFace

def verification_facial(path1, path2):
    """
    Vérifie la similarité faciale entre deux chemins de fichiers.
    path1 : Chemin de l'image stockée dans le modèle
    path2 : Chemin de l'image téléchargée (fichier temporaire)
    """
    try:
        # 0.6 est le seuil standard pour VGG-Face (modèle par défaut)
        result = DeepFace.verify(
            img1_path = path1, 
            img2_path = path2,
            model_name = "VGG-Face",
            threshold = 0.6
        )
        return result['verified']

    except Exception as e:
        print(f"Erreur lors de la vérification DeepFace: {e}")
        return False
    finally:
        # Supprime le fichier temporaire une fois la vérification terminée
        if os.path.exists(path2):
            os.unlink(path2)


def generate_receipt_pdf_in_memory(data):
    """
    Génère le PDF de la quittance de loyer dans un buffer BytesIO.
    """
    buffer = io.BytesIO()
    
    # Configuration du Document
    doc = SimpleDocTemplate(
        buffer,  # Écrit dans le buffer
        pagesize=A4,
        rightMargin=50, leftMargin=50,
        topMargin=50, bottomMargin=50
    )
    elements = []
    styles = getSampleStyleSheet()

    # Définition des Styles Personnalisés (Utilisant FONT_NAME et BOLD_FONT_NAME)
    styles.add(ParagraphStyle(name='DefaultText', parent=styles['Normal'], fontName=FONT_NAME))
    styles.add(ParagraphStyle(name='TitleStyle', parent=styles['Heading1'], fontSize=28, alignment=1, spaceAfter=15, fontName=BOLD_FONT_NAME, textColor=colors.HexColor('#000')))
    styles.add(ParagraphStyle(name='SubtitleStyle', parent=styles['DefaultText'], fontSize=13, alignment=1, spaceAfter=30, textColor=colors.HexColor('#666666')))
    styles.add(ParagraphStyle(name='MainText', parent=styles['DefaultText'], fontSize=15, alignment=4, leading=22, spaceAfter=30))
    styles.add(ParagraphStyle(name='InfoSection', parent=styles['DefaultText'], fontSize=13, leading=18))
    styles.add(ParagraphStyle(
        name='SignatureTextStyle',
        parent=styles['DefaultText'],
        fontSize=12, 
        fontName=BOLD_FONT_NAME 
    ))
    qr_text_style = styles['DefaultText']
    qr_text_style.alignment = 1 
    qr_text_style.fontSize = 8 
    
    elements.append(Paragraph(data["titre"], styles['TitleStyle']))
    elements.append(Paragraph(data["sous_titre"], styles['SubtitleStyle']))
    
    info_table_data = [
        [Paragraph(f'<font name="{BOLD_FONT_NAME}" size="13" color="#111">Nom et Prénom du Locataire :</font> {data["nom_locataire"]}', styles['InfoSection'])],
        [Paragraph(f'<font name="{BOLD_FONT_NAME}" size="13" color="#111">Adresse du bien loué :</font> {data["adresse_locataire"]}', styles['InfoSection'])],
        [Paragraph(f'<font name="{BOLD_FONT_NAME}" size="13" color="#111">Mois et Année concernés :</font> {data["mois_annee"]}', styles['InfoSection'])],
    ]
    info_table = Table(info_table_data, colWidths=[7 * inch])
    info_table.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0)]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.2 * inch))

    amount_text = (
        f'<font name="{BOLD_OBLIQUE_FONT_NAME}" size="14" color="#2a6a2a">'
        f'{data["montant_lettres"]} ({data["montant_chiffres"]})'
        f'</font>'
    )


    body_text_1 = (
        f'Le soussigné, bailleur, déclare avoir reçu de <b>{data["nom_locataire"]}</b>, locataire du bien '
        f'mentionné ci-dessus, la somme de {amount_text} pour le paiement du loyer du '
        f'mois de <b>{data["mois_annee"]}</b>.'
    )
    
    body_text_2 = '<font size="12" color="#000">Cette quittance a été établie pour servir et faire valoir ce que de droit.</font>'
    
    elements.append(Paragraph(body_text_1, styles['MainText']))
    elements.append(Paragraph(body_text_2, styles['MainText'])) # L'erreur se produit ici


    
    elements.append(Paragraph(f'Fait à <b>{data["ville_fait"]}</b>, le {data["date_fait"]}', styles['DefaultText']))
    elements.append(Spacer(1, 0.2 * inch))

    # --- Section Signature ---
    try:
        
        signature_image = Image(get_font_path(data["signature"]), width=2*inch, height=0.8*inch)
    except Exception:
        signature_image = Paragraph('Pas de signature (Image manquante)', styles['SignatureTextStyle'])

    COL_WIDTH_LOCATAIRE = 3.5 * inch
    COL_WIDTH_BAILLEUR = 3.5 * inch
    
    signature_table_data = [
        ["", signature_image],
        [Paragraph("Signature du Locataire", styles['SignatureTextStyle']), 
         Paragraph("Signature du Bailleur", styles['SignatureTextStyle'])],
    ]
    
    signature_table = Table(signature_table_data, 
                            colWidths=[COL_WIDTH_LOCATAIRE, COL_WIDTH_BAILLEUR], 
                            rowHeights=[0.8*inch, None]) 
                            
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'), 
        ('VALIGN', (0,0), (-1,0), 'BOTTOM'),
        ('VALIGN', (0,1), (-1,1), 'TOP'),
        ('LINEABOVE', (0,1), (0,1), 1, colors.black),
        ('LINEABOVE', (1,1), (1,1), 1, colors.black),
        ('TOPPADDING', (1,0), (1,1), 1),
        ('BOTTOMPADDING', (1,0), (1,1), 1),
    ]))
    
    elements.append(signature_table)
    elements.append(Spacer(1, 0.2 * inch)) 
    
    # --- Section QR Code ---
    try:
        
        qr_code_image = Image(get_font_path(data["qr"]), width=0.8*inch, height=0.8*inch) 
        qr_code_image.hAlign = 'CENTER'
        elements.append(qr_code_image)
    except Exception:
        elements.append(Paragraph("Erreur: QR Code non trouvé.", qr_text_style))

    verification_link = data["lien"]
    elements.append(Paragraph(verification_link, qr_text_style))
    elements.append(Spacer(1, 0.1 * inch))
   
    # Ligne d'enregistrement : construit le PDF dans le buffer
    doc.build(elements)
    
    buffer.seek(0)
    
    return buffer


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

@login_required(login_url='login')
def enregistrer_quittance(request, id=None):
    
    if request.method == 'POST':
        
        password_str = request.POST.get('password')
        private_key_file = request.FILES.get('private_key')
        base64_data = request.POST.get('verification_faciale')
        
        # Vérification minimale des données critiques
        if not password_str or not private_key_file or not base64_data:
            messages.error(request, "Mot de passe, clé privée ou capture faciale manquant(e).")
            return redirect(reverse('view_quittance', kwargs={'id': id}))

        # Décodage Base64 et création de fichier temporaire pour DeepFace
        path_image_temp = None
        est_verifie = False
        
        try:
            # Nettoyage et décodage Base64
            if ';base64,' in base64_data:
                format_separator = base64_data.find(';base64,')
                base64_content = base64_data[format_separator + 8:]
            else:
                base64_content = base64_data

            image_data = base64.b64decode(base64_content)

            # Créer un Fichier Temporaire pour DeepFace
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpeg') as tmp:
                tmp.write(image_data)
                path_image_temp = tmp.name 

            # Obtenir le chemin de l'image du modèle pour la vérification
            path_image_modele = request.user.security.verification_faciale.path 
            
            # Exécuter la vérification faciale
            # NOTE: La fonction verification_facial doit gérer la suppression de path_image_temp si nécessaire,
            # mais nous la faisons ici dans le 'finally' pour la robustesse.
            est_verifie = verification_facial(path_image_modele, path_image_temp)

        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la vérification faciale/traitement de l'image : {e}")
            return redirect(reverse('view_quittance', kwargs={'id': id}))
        finally:
            # Nettoyage du fichier temporaire capturé
            if path_image_temp and os.path.exists(path_image_temp):
                os.unlink(path_image_temp)
        
        # --------------------------------------------------------
        # LOGIQUE SI LA VÉRIFICATION FACIALE A RÉUSSI
        # --------------------------------------------------------
        if est_verifie:
            
            # 2.1. Récupération des données du Loyer
            try: 
                loyer = Loyer.objects.get(id=id)
                property = loyer.property
                mois_map = {"1":'Janvier','2':'Février','3':'Mars','4':'Avril','5':'Mai','6':'Juin','7':'Juillet','8':'Août','9':'Séptembre','10':'Octobre','11':'Novembre','12':'Décembre'}
                month = mois_map[str(loyer.mois)] + ' ' + str(loyer.annee)
            except Loyer.DoesNotExist:
                return HttpResponse('Erreur : Loyer non trouvé (ID incorrect)')
            except Exception:
                return HttpResponse('Erreur lors de la récupération des données de base')

            montant = convertir_nombre_en_texte_francais(loyer.montant) + ' dollars américains'
            signature_path_absolu = None
            qr_path_absolu = None

            if request.user.security.signature:
                signature_path_absolu = request.user.security.signature.path
            if loyer.qr_document:
                qr_path_absolu = loyer.qr_document.path
                
            receipt_data = {
                "titre": "Récus Paiement Loyer",
                "sous_titre": "Document officiel pour le paiement du loyer",
                "nom_locataire": property.nom_complet_occupant,
                "adresse_locataire": property.adresse,
                "mois_annee": month,
                "nom_bailleur": request.user.username, 
                "montant_lettres": montant ,
                "montant_chiffres": str(loyer.montant) + ' USD',
                "date_fait": loyer.date_payement,
                "ville_fait": "Kinshasa",
                "qr": qr_path_absolu,
                "signature" : signature_path_absolu,
                "lien": "http://172.20.10.3:8000/verify/" + loyer.code
            }
            
            # 2.2. Génération et Enregistrement du PDF
            p12_path = None
            try:
                # Générer PDF
                pdf_buffer = generate_receipt_pdf_in_memory(receipt_data)
                pdf_buffer.seek(0) 

                timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
                locataire_safe = receipt_data['nom_locataire'].replace(' ', '_').replace('.', '')
                filename = f"Quittance_{locataire_safe}_{timestamp}.pdf"
                content_file = ContentFile(pdf_buffer.read())
                
                # Enregistrer le FileField (crée le fichier sur le disque)
                loyer.url_document.save(filename, content_file)
                pdf_path_on_disk = loyer.url_document.path 
                
                # --- PROCESSUS DE SIGNATURE (Cryptographie) ---
                cert_path = request.user.security.cle_publique.path 
                password_bytes = password_str.encode('utf-8')

                # 1) Charger la clé privée
                private_key_file.seek(0) 
                private_key_content = private_key_file.read()
                cle_privee = serialization.load_pem_private_key(
                    private_key_content, 
                    password=password_bytes,
                    backend=default_backend()
                )
                
                # 2) Chargement du certificat PEM
                with open(cert_path, "rb") as cf:
                    certificat = x509.load_pem_x509_certificate(cf.read(), default_backend())

                # 3) Créer un PKCS#12 temporaire
                p12_path = creer_pkcs12_temp(cle_privee, certificat, password_bytes)

                # 4) Chargement du signataire (SimpleSigner)
                try:
                    signer = signers.SimpleSigner.load_pkcs12(p12_path, passphrase=password_bytes)
                except AttributeError:
                    signer = signers.SimpleSigner.load_pkcs12(p12_path, password=password_bytes)

                # 5) Signer le PDF
                with open(pdf_path_on_disk, 'rb') as doc: 
                    writer = IncrementalPdfFileWriter(doc)
                    meta = PdfSignatureMetadata(
                        field_name='Signature_Securisee',
                        reason='Reçu signé numériquement',
                        location='Kinshasa, CD'
                    )
                    signed_buffer = signers.sign_pdf(writer, meta, signer=signer)
                    signed_pdf_data = signed_buffer.read() 

                # Écraser l'ancien PDF avec la version signée
                with open(pdf_path_on_disk, 'wb') as fout:
                    fout.write(signed_pdf_data)
                    
                # 6) Ancrage Hedera
                ancrage_succes = ancre_hedera(request, loyer)

                if ancrage_succes:
                    messages.success(request, f"✅ Quittance pour {month} enregistrée, signée et ANCRÉE sur Hedera avec succès.")
                    return redirect(reverse('succes_enregistrement_quittance', kwargs={'id': loyer.id}))
                else:
                    messages.error(request, "❌ Signature PDF réussie, mais échec de l'ancrage Hedera.")
                    return redirect(reverse('view_quittance', kwargs={'id': id}))

            except Exception as e:
                messages.error(request, f"❌ Erreur critique pendant la signature/sauvegarde : {e}")
                return redirect(reverse('view_quittance', kwargs={'id': id}))
            finally:
                # Nettoyage du fichier p12 temporaire
                if p12_path and os.path.exists(p12_path):
                    try:
                        os.remove(p12_path)
                    except Exception:
                        pass
        else:
            # --------------------------------------------------------
            # ÉCHEC DE LA VÉRIFICATION FACIALE
            # --------------------------------------------------------
            messages.error(request, "❌ Échec de la vérification faciale. Accès refusé.")
            return redirect(reverse('view_quittance', kwargs={'id': id}))

    # --------------------------------------------------------
    # Requête GET
    # --------------------------------------------------------
    return redirect(reverse('view_quittance', kwargs={'id': id}))



def succes_enregistrement_quittance(request, id):
    loyer = get_object_or_404(Loyer, id=id)
    filename = os.path.basename(loyer.url_document.name)
     
    
    context = {
        'loyer': loyer, 
        'filename': filename,
        'HCS_TOPIC_ID': settings.HCS_TOPIC_ID, 
    }#
    
    
    return render(request, 'immobilier/succes_quittance.html', context)

@login_required(login_url='login')
def succes_enregistrement_quittancee(request,id):
    """
    Récupère la dernière quittance enregistrée par l'utilisateur
    et passe son URL au template.
    """
    try:
        
        # 🚨 ON RÉCUPÈRE LE DERNIER DOCUMENT CRÉÉ PAR L'UTILISATEUR 🚨
        derniere_quittance = Loyer.objects.get(id=id)
        try:
            topic_id_str = settings.HCS_TOPIC_ID.toString() # <-- UTILISER .toString()
        except AttributeError:
        # Si HCS_TOPIC_ID est déjà une string, on la garde.
            topic_id_str = settings.HCS_TOPIC_ID
        
        context = {
            # Passe l'URL relative du fichier (ex: /media/quittances/...)
            'pdf_url': derniere_quittance.url_document.url,
            'filename': derniere_quittance.url_document.name.split('/')[-1] # Nom du fichier pour le bouton
        }
    except Loyer.DoesNotExist:
        
        context = {
            'pdf_url': None,
            'message_erreur': "Aucune quittance n'a été trouvée."
        }
        
    return render(request, 'immobilier/succes_quittance.html', context)