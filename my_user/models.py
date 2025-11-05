from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from core.models import BaseImage
import os
import uuid



def upload_to_unique_uuid(instance, filename):
        ext = filename.split('.')[-1]
        filename_unique = f"{uuid.uuid4().hex[:8]}.{ext}"
        return os.path.join('video_presentation', filename_unique)
    


class MyUser(AbstractUser):
    username = models.CharField(max_length=25, null=False, blank=True)
    numero_tel = models.CharField(max_length=30, null=True,unique=True)
    email =models.EmailField(null=True,blank=True)
    email_authenticate=models.BooleanField(blank=True, null=True,default=False)
    sexe = models.CharField(max_length=10,null=False,default='homme')
    USERNAME_FIELD='numero_tel'
    def __str__(self):
         return '{}_{}'.format(self.id,self.username)
    



#class PermissionBlog
class ProfileUser(models.Model):
    contact_telephone = models.CharField(max_length=25, blank=True, null=True)
    user = models.OneToOneField(MyUser, related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    commune = models.CharField(max_length=255, blank=True, null=True)
    rue = models.CharField(max_length=255, blank=True, null=True)
    numero_rue = models.CharField(max_length=155, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    date_mise_a_jour = models.DateField(auto_now=True)
    type_compte = models.CharField(max_length=20,blank=True, default='User')
    email =models.EmailField(null=True, blank=True)
   


class ImageProfil(BaseImage):
    image = models.ImageField(upload_to=BaseImage.upload_to_unique_uuid, null=True)
    user = models.OneToOneField(MyUser, related_name='image',on_delete=models.CASCADE, null=True)
   # blog = models.OneToOneField(Blog, related_name='image',on_delete=models.CASCADE, null=True)
    video = models.FileField(upload_to=upload_to_unique_uuid, null=True) 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'myUser/images_profile/'



class Revenus(models.Model):
    montant = models.FloatField(null=True, blank=False)
    description = models.CharField(max_length=500, blank=True, null=True)

    date_revenu = models.DateField(null=True)
    """ex: "Ventes_nourriture", "Ventes_boissons", 
"Service_traiteur", "Pourboires"). """
    name  = models.CharField(max_length=25,default='')
    user = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True, related_name='revenus')
    def __str__(self):
        return self.name +' '+ self.user.username

class Depenses(models.Model):
    montant = models.FloatField(null=True, blank=False)
    date_depense = models.DateField(null=True)
    description = models.CharField(max_length=500,blank=True,null=True)
    
    name  = models.CharField(max_length=25,default='')
    user = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True, related_name='depenses')
    
    def __str__(self):
        return self.name +' '+ self.user.username
    

class Dettes(models.Model):
    montant = models.FloatField(null=True, blank=False)
    date_dettes = models.DateField(null=True,blank=True)
    description = models.CharField(max_length=500,blank=True,null=True)
    datte_rembourssement =  models.DateField(null=True,blank=True)

    user = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True, related_name='dettes')
    
    def __str__(self):
        return self.name +' '+ self.user.username
    
class Secutity(models.Model):
    #cle_publique = models.CharField(max_length=2000, blank=True,null=True)
    cle_publique = models.FileField(upload_to='certificats_publiques/', blank=True, null=True)
    signature = models.ImageField(upload_to='signature/')
    verification_faciale = models.ImageField(upload_to='image_faciale/',null=True,blank=True)

    # Informatio de paiement
    id_hedera = models.CharField(max_length=255,blank=True,null=True)
    numero_bancaire = models.CharField(max_length=255,blank=True,null=True)
    paiement_mobile = models.CharField(max_length=255,blank=True,null=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    user = models.OneToOneField(
        MyUser,
        related_name='security',
        on_delete=models.CASCADE)
    

class DocumentSigne(models.Model):
    """
    Modèle pour stocker les documents PDF signés numériquement et ancrés sur Hedera.
    """
    
    # --- Informations du Document Signé ---
    
    # Le fichier PDF signé, stocké sur le serveur
    document_signe = models.FileField(
        upload_to='documents_signes/',
        verbose_name="Document PDF Signé"
    )
    
    # Description ou type du document (ex: 'Quittance de Loyer', 'Contrat de Travail')
    type_document = models.CharField(
        max_length=100,
        verbose_name="Type de Document"
    )
    
    # Hash du document (preuve que le contenu n'a pas changé)
    document_hash_sha256 = models.CharField(
        max_length=64, # SHA-256 produit 64 caractères hexadécimaux
        verbose_name="Hash SHA-256 (Ancrage)"
    )
    
    # --- Preuve Hedera Hashgraph (HCS) ---

    # Le Consensus Time d'Hedera (preuve temporelle)
    hedera_timestamp = models.CharField(
        max_length=255, 
        unique=True, # Le timestamp doit être unique pour la preuve
        verbose_name="Horodatage Hedera (Consensus Time)"
    )
    
    # L'ID de la transaction Hedera (pour la vérification en ligne)
    hedera_transaction_id = models.CharField(
        max_length=255,
        verbose_name="ID de Transaction Hedera"
    )
    
    # Lien public pour vérifier la transaction Hedera (ex: Hedera Explorer)
    lien_verification_hedera = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Lien de Vérification Hedera"
    )
    
    # --- Liens avec l'Utilisateur ---
    
    # Lien vers l'utilisateur qui a signé le document (pour savoir QUI a signé)
    signataire = models.ForeignKey(
        MyUser, # Utiliser le modèle utilisateur par défaut ou MyUser
        related_name='documents_signes',
        on_delete=models.CASCADE,
        verbose_name="Signataire"
    )
    
    # Champ pour gérer le statut (Optionnel mais utile)
    statut = models.CharField(
        max_length=50,
        default='SIGNÉ & ANCRÉ',
        verbose_name="Statut du Document"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_document} - Signé par {self.signataire.username}"

    class Meta:
        verbose_name = "Document Signé"
        verbose_name_plural = "Documents Signés"
        # Ajout d'une contrainte d'unicité sur le hash pour éviter de signer deux fois
        # le même contenu (si le fichier n'a pas changé, le hash est le même)
        constraints = [
            models.UniqueConstraint(fields=['document_hash_sha256'], name='unique_document_hash')
        ]


