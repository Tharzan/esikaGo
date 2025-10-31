from django.db import models
from core.models import BaseImage
from blog.models import Blog
from my_user.models import MyUser


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


    observation = models.CharField(
        max_length=50,blank=True, 
        default='totalite')
    
    property = models.ForeignKey(
        SaveProperty, 
        related_name='historique',
        blank=True,null=True,
        on_delete=models.CASCADE)
    
    annee = models.IntegerField(default=2025)
    tp_hedera = models.CharField(max_length=50,blank=True, default='')
    ancre_hedera = models.CharField(max_length=500,blank=True, default='')
    hash_document = models.CharField(max_length=500,blank=True, default='')
    lien_document = models.FileField(upload_to='immobilier/recus/',blank=True,null=True)
    def __str__(self):
        return f"Moid de {self.mois} id: {self.id} et adresse {self.property.adresse}"


    class Meta:
        # L'ordre de tri par défaut (Default ordering)
        # 1. '-annee' : Trie par année décroissante (du plus grand, ex: 2025, au plus petit, ex: 2024)
        # 2. 'mois' : Trie par mois croissant (du plus petit, ex: 1, au plus grand, ex: 12)
        ordering = ['-annee', 'mois']