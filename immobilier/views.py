from django.shortcuts import render,HttpResponse, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from immobilier.models import ImageMaisons
from immobilier.forms import *
from django.contrib import messages
from blog.models import BlogAdministrateur
import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os 
from reportlab.lib.pagesizes import landscape

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
                nouveau_loyer.save()
                
                
                
                return redirect(reverse('historique_maison', kwargs={'id': property.id}))
                        
            
            else:

                return render(request,'immobilier/historique_maison.html',{'form': form,'liste_annees':liste_annees, 'formError':True,'payement':historique,'has_historique':has_historique})
        
        else:
            
            return render(request,'immobilier/historique_maison.html', {'liste_annees':liste_annees,'form': form,'payements':historique,'has_historique':has_historique})   


from num2words import num2words

def convertir_nombre_en_texte_francais(nombre):
    
    try:
        # 'lang='fr'' essentiel pour obtenir la traduction en français.
        texte_resultat = num2words(nombre, lang='fr')
        return texte_resultat
    except:
        return "Erreur"


@login_required    
def view_quittance(request,id):
    
        quittance = Loyer.objects.get(id=int(id))
        property = quittance.property
        services_map = {
            'montant': 'montant',
            'date_payement': 'date_payement',
            'mois': 'mois',
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

        return render(request,'immobilier/view_quittance.html', {'recus': recus})   

   


def siger_recu(request,id):
    
    quittance = Loyer.objects.get(id=id)
    property = quittance.property
    file = 'rrrr'
    # --- 0. Configuration des Polices et de la Taille de Page ---

    # Taille de page compacte (7.5 pouces de large x 6.0 pouces de haut)
    RECEIPT_WIDTH = 7.5 * inch    
    RECEIPT_HEIGHT = 8.0 * inch   
    CUSTOM_RECEIPT_SIZE = (RECEIPT_WIDTH, RECEIPT_HEIGHT)

    # Enregistrement de la Police Georgia (avec gestion d'erreur)
    try:
        # Assurez-vous que les fichiers .ttf sont dans le répertoire du script
        pdfmetrics.registerFont(TTFont('Georgia', 'georgia.ttf'))
        pdfmetrics.registerFont(TTFont('Georgia-Bold', 'georgiab.ttf'))
        pdfmetrics.registerFont(TTFont('Georgia-Italic', 'georgiai.ttf'))
        pdfmetrics.registerFont(TTFont('Georgia-BoldItalic', 'georgiaz.ttf'))
        
        FONT_NAME = 'Georgia'
        BOLD_FONT_NAME = 'Georgia-Bold'
        BOLD_OBLIQUE_FONT_NAME = 'Georgia-BoldItalic'

    except Exception:
        print("Avertissement: Polices Georgia non trouvées. Utilisation de Times-Roman.")
        FONT_NAME = 'Times-Roman'
        BOLD_FONT_NAME = 'Times-Bold'
        BOLD_OBLIQUE_FONT_NAME = 'Times-BoldItalic'
    mois_paiement ={"1":'Janvier','2':'Février','3':'Mars',
            '4':'Avril','5':'Mai','6':'Juin','7':'Juillet','8':'Août','9':'Séptembre',
            '10':'Octobre','11':'Novembre','12':'Décembre'}
    # --- 1. Définir les Données du Reçu ---
    data = {
        "titre": "Quittance de Loyer",
        "sous_titre": "Document officiel pour le paiement du loyer",
        "nom_locataire": request.username,
        "adresse_locataire": property.type_bien,
        "mois_annee": mois_paiement[str(quittance.mois)],
        "nom_bailleur": property.nom_complet_occupant,
        "montant_lettres": convertir_nombre_en_texte_francais(int(quittance.montant)),
        "montant_chiffres": quittance.montant,
        "date_fait": quittance.date_payement,
        "ville_fait": "Kinshasa",
    }

    
        # Configuration du Document avec la taille COMPACTE
    doc = SimpleDocTemplate(
            file, 
            pagesize=CUSTOM_RECEIPT_SIZE, 
            rightMargin=30, leftMargin=30,
            topMargin=30, bottomMargin=30
        )
    elements = []
    styles = getSampleStyleSheet()

        # Définition des Styles Personnalisés
    styles.add(ParagraphStyle(name='DefaultText', parent=styles['Normal'], fontName=FONT_NAME))
    styles.add(ParagraphStyle(name='TitleStyle', parent=styles['Heading1'], fontSize=24, alignment=1, spaceAfter=15, fontName=BOLD_FONT_NAME, textColor=colors.HexColor('#333333')))
    styles.add(ParagraphStyle(name='SubtitleStyle', parent=styles['DefaultText'], fontSize=13, alignment=1, spaceAfter=30, textColor=colors.HexColor('#666666')))
    styles.add(ParagraphStyle(name='MainText', parent=styles['DefaultText'], fontSize=12, alignment=4, leading=22, spaceAfter=30))
        # Labels en gras dans la section info (fontSize: 11)
    styles.add(ParagraphStyle(name='InfoSection', parent=styles['DefaultText'], fontSize=11, leading=18, spaceAfter=5))
        
        # Style pour la signature (Taille 14pt)
    styles.add(ParagraphStyle(
            name='SignatureTextStyle',
            parent=styles['DefaultText'],
            fontSize=14, 
            fontName=BOLD_FONT_NAME 
        ))
        
        # Style du texte du QR code
    qr_text_style = styles['DefaultText']
    qr_text_style.alignment = 1 # Centrer
    qr_text_style.fontSize = 8 
        
        # --- 2. Construction du Document ---
    elements.append(Paragraph(data["titre"], styles['TitleStyle']))
    elements.append(Paragraph(data["sous_titre"], styles['SubtitleStyle']))
        
        # --- Info Section : Labels en gras ---
        # La largeur totale du contenu est (7.5 - 2*0.3) = 6.9 pouces
    CONTENT_WIDTH = 6.9 * inch

    info_table_data = [
            # Les labels sont entre <b></b> pour le gras
            [Paragraph(f"<b>Nom et Prénom du Locataire :</b> {data['nom_locataire']}", styles['InfoSection'])],
            [Paragraph(f"<b>Adresse du bien loué :</b> {data['adresse_locataire']}", styles['InfoSection'])],
            [Paragraph(f"<b>Mois et Année concernés :</b> {data['mois_annee']}", styles['InfoSection'])],
        ]
    info_table = Table(info_table_data, colWidths=[CONTENT_WIDTH]) 
    info_table.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0)]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.2 * inch))

        # --- Texte principal ---
    amount_text = (
            f'<font name="{BOLD_OBLIQUE_FONT_NAME}" size="14" color="#2a6a2a">'
            f'{data["montant_lettres"]} ({data["montant_chiffres"]})'
            f'</font>'
        )
        # Correction: Assurez-vous d'inclure les deux noms (bailleur et locataire) dans la phrase
    body_text_1 = (
            f'Le soussigné, bailleur, déclare avoir reçu de <b>{data["nom_locataire"]}</b>, locataire du bien '
            f'mentionné ci-dessus, la somme de {amount_text} pour le paiement du loyer du '
            f'mois de <b>{data["mois_annee"]}</b>.'
        )
    body_text_2 = "Cette quittance a été établie pour servir et faire valoir ce que de droit."
    elements.append(Paragraph(body_text_1, styles['MainText']))
    elements.append(Paragraph(body_text_2, styles['MainText']))
        
    elements.append(Paragraph(f'Fait à <b>{data["ville_fait"]}</b>, le {data["date_fait"]}', styles['DefaultText']))
    elements.append(Spacer(1, 0.2 * inch))

        # --- Signature Section ---
    try:
            # Tenter de charger l'image de signature du Bailleur
            signature_image = Image('2222.jpg', width=1.5*inch, height=0.4*inch) 
    except Exception:
            # Solution de repli si l'image manque
            signature_image = Paragraph("", styles['DefaultText'])
        
        # Largeur de colonne ajustée à la largeur totale (6.9 pouces)
    COL_WIDTH_LOCATAIRE = CONTENT_WIDTH / 2.0
    COL_WIDTH_BAILLEUR = CONTENT_WIDTH / 2.0
        
    signature_table_data = [
            ["", signature_image], # Image Bailleur
            [Paragraph("Signature du Locataire", styles['SignatureTextStyle']), 
            Paragraph("Signature du Bailleur", styles['SignatureTextStyle'])],
        ]
        
    signature_table = Table(signature_table_data, 
                                colWidths=[COL_WIDTH_LOCATAIRE, COL_WIDTH_BAILLEUR], 
                                rowHeights=[0.5*inch, None]) 
                                
    signature_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,-1), 'CENTER'), # Locataire: CENTRE
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),  # Bailleur: DROITE
            ('VALIGN', (0,0), (-1,0), 'BOTTOM'), 
            ('VALIGN', (0,1), (-1,1), 'TOP'), 
            ('LINEABOVE', (0,1), (0,1), 1, colors.black), 
            ('LINEABOVE', (1,1), (1,1), 1, colors.black), 
            ('TOPPADDING', (1,0), (1,1), 1),
            ('BOTTOMPADDING', (1,0), (1,1), 1),
        ]))
        
    elements.append(signature_table)

        # --- 3. AJOUT DU QR CODE EN BAS ---
    elements.append(Spacer(1, 0.2 * inch)) 
        
    try:
            # Charger l'image du QR code et la centrer
            qr_code_image = Image('858f8fce.png', width=0.8*inch, height=0.8*inch) 
            qr_code_image.hAlign = 'CENTER'
            elements.append(qr_code_image)
    except Exception:
            print("Erreur: QR Code '858f8fce.png' non trouvé.")

        # Texte de vérification
    verification_link = "Lien de vérification: 127.0.0.1:8000/viewQuittance/6/"
    elements.append(Paragraph(verification_link, qr_text_style))
    elements.append(Spacer(1, 0.1 * inch))

        # 4. Générer le PDF
    doc.build(elements)
        


    