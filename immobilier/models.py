from django.db import models
from core.models import BaseImage
from blog.models import Blog
from my_user.models import MyUser
from django.utils.translation import gettext_lazy as _

from core.models import BaseImage
import uuid
import os
from django.utils.text import slugify 
import qrcode
import io
from django.core.files.base import ContentFile
import json
   
class SaveProperty(models.Model):
    type_bien = models.CharField(max_length=25, null=True,blank=True)
    user = models.ForeignKey(MyUser, null=True,on_delete=models.CASCADE, related_name='property')
    adresse = models.CharField(max_length=255,default='-')
    
    statut = models.CharField(max_length=25, null=True,blank=True)
    montant = models.IntegerField(null=True, blank=True)
    devise_payement = models.CharField(max_length=25, default='$',blank=True)
    id_maison  = models.CharField(max_length=25, null=True,blank=True)
    nom_complet_occupant = models.CharField(max_length=255, null=True,blank=True)
    tel_occupant = models.CharField(max_length=25, null=True,blank=True)
    date_entrer = models.DateField(blank=True, null=True)
    garantie = models.IntegerField(null=True, blank=True)
    devise_garantie = models.CharField(max_length=25, default='$',blank=True)
    contratBail = models.FileField(null=True, blank=True, upload_to='document/')
    mail_occupant = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} property {self.id} {self.adresse}"

class PostMaison(models.Model):
    pays = models.CharField(max_length=25,  default='RDC', blank=True)
    ville = models.CharField(max_length=25, default='kinshasa', blank=True)
    commune = models.CharField(max_length=25, null=False, blank=False)
    type_bien = models.CharField(max_length=25, null=True,blank=True)
    nombre_chambre = models.IntegerField(null=True, blank=True)
    nombre_piece = models.IntegerField(null=True, blank=True)
    nombre_douche = models.IntegerField(null=True, blank=True)
    description = models.CharField(max_length=500, null=True,blank=True)
    price = models.IntegerField()
    
    has_balcony = models.BooleanField(blank=True, null=True)
    has_terasse = models.BooleanField(blank=True, null=True)
    has_parking =  models.BooleanField(blank=True, null=True)
    maisons_meuble =  models.BooleanField(blank=True, null=True)
    cuisine_meuble = models.BooleanField(blank=True, null=True)
    cuisine = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.description
    

    
class ImageMaisons(BaseImage):
    image = models.ImageField(upload_to=BaseImage.upload_to_unique_uuid)
    post_maison  = models.ForeignKey(PostMaison, on_delete=models.CASCADE)
   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.url = 'immobilier/images_maisons/'
        
    def __str__(self):
       return self.image.url
    
class Loyer(models.Model):
    montant = models.IntegerField()
    date_payement = models.DateField()
    mois = models.IntegerField(default=1)
    signer = models.BooleanField(default=False)

    observation = models.CharField(
        max_length=50,blank=True, 
        default='totalite')
    
    property = models.ForeignKey(
        SaveProperty, 
        related_name='historique',
        blank=True,null=True,
        on_delete=models.CASCADE)
    
    annee = models.IntegerField(default=2025)
    
    
    code = models.CharField(
        max_length=500,
        blank=True,
         default='')

    url_document = models.FileField(
        verbose_name=_("Fichier Quittance PDF"),
        upload_to='quittances/%Y/%m/',
        help_text=_("Lien vers le fichier PDF généré de la quittance."),
        null=True,
        blank=True,
    )
    qr_document = models.ImageField(
        upload_to=BaseImage.upload_to_unique_uuid, 
        null=True, 
        blank=True
    )

    
    type_document = models.CharField(
        max_length=100,
        verbose_name="Type de Document",
        blank=True,
        default='quittance'
    )
    
    document_hash_sha256 = models.CharField(
        max_length=64, 
        verbose_name="Hash SHA-256 (Ancrage)",
        blank=True,
        default='PENDING'
    )
    
    # --- Preuve Hedera Hashgraph (HCS) ---

    # Le Consensus Time d'Hedera (preuve temporelle)
    hedera_timestamp = models.CharField(
        max_length=255, 
        
        verbose_name="Horodatage Hedera (Consensus Time)",
        blank=True,
        default='PENDING'

    )
    
    # L'ID de la transaction Hedera (pour la vérification en ligne)
    hedera_transaction_id = models.CharField(
        max_length=255,
        verbose_name="ID de Transaction Hedera",
        null=True,
        blank=True,
    )
    
    # Lien public pour vérifier la transaction Hedera 
    lien_verification_hedera = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Lien de Vérification Hedera"
    )
    
    # --- Liens avec l'Utilisateur ---
    
    signataire = models.ForeignKey(
        MyUser, 
        related_name='quittance_signes',
        on_delete=models.CASCADE,
        verbose_name="Signataire",
        null=True,
    )
    
    statut = models.CharField(
        max_length=50,
        default='',
        verbose_name="Statut du Document"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)

    


    
    def __str__(self):
        return f"Moid de {self.mois} id: {self.id} et adresse {self.property.adresse}"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'document_qr/'

    def image_qr(self,data):
        
        qr = qrcode.QRCode(
        version=2,  
        error_correction=qrcode.constants.ERROR_CORRECT_L,  
        box_size=20,  
        border=4,)

        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="rgb(0,0,125)", back_color="white")
        
        img_io = io.BytesIO()
        img.save(img_io,format='PNG')
        img_file = ContentFile(img_io.getvalue(), name='qr_code.png')

        self.qr_document.save('qr_code.png', img_file,save=False)

    

    class Meta:
        # L'ordre de tri par défaut (Default ordering)
        # 1. '-annee' : Trie par année décroissante (du plus grand, ex: 2025, au plus petit, ex: 2024)
        # 2. 'mois' : Trie par mois croissant (du plus petit, ex: 1, au plus grand, ex: 12)
        ordering = ['-annee', 'mois']






class Document(models.Model):
    
    # 1. Champ pour le fichier PDF
    # Le fichier sera stocké dans un sous-dossier MEDIA_ROOT/quittances/AAAA/MM/
    # Ex: media/quittances/2025/11/Quittance_Jean_K_20251101_113000.pdf
    url_document = models.FileField(
        verbose_name=_("Fichier Quittance PDF"),
        upload_to='quittances/%Y/%m/',
        help_text=_("Lien vers le fichier PDF généré de la quittance.")
    )

    # 2. Champs de traçabilité (Qui a généré le document ?)
    bailleur = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='quittances_emises',
        verbose_name=_("Bailleur / Émetteur")
    )
    

    # 3. Champs d'information et de date
    montant_paye = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_("Montant Payé")
    )
    
    mois_concerne = models.CharField(
        max_length=50,
        verbose_name=_("Mois et Année Concernés")
    )

    cree_le = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date de Création")
    )

    def __str__(self):
        return f"Quittance - {self.mois_concerne} - {self.bailleur.username}"

    class Meta:
        verbose_name = _("Document (Quittance)")
        verbose_name_plural = _("Documents (Quittances)")
        ordering = ['-cree_le']