from django.db import models
from core.models import BaseImage
from my_user.models import MyUser
import uuid
import os
from django.utils.text import slugify 
import qrcode
import io
from django.core.files.base import ContentFile
import json

def upload_to_unique_uuid(instance, filename):
        ext = filename.split('.')[-1]
        filename_unique = f"{uuid.uuid4().hex[:8]}.{ext}"
        return os.path.join('video_presentation/blog', filename_unique)

def upload_to_unique_uuid_image(instance, filename):
        ext = filename.split('.')[-1]
        filename_unique = f"{uuid.uuid4().hex[:8]}.{ext}"
        return os.path.join('blog/images_profile', filename_unique)
    

class Blog(models.Model):
    name = models.CharField(max_length=30)
    type_page = models.CharField(max_length=25)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True,blank=True)
    note = models.IntegerField(blank=True, default=0)
    nombre_avis = models.IntegerField(blank=True,default=0)
    date_mise_a_jour =  models.DateTimeField(auto_now=True)
    date_creation = models.DateField(auto_now_add=True)
    status = models.CharField(default='actif',blank=True)
    #statut (Texte): Le statut du restaurant dans votre système (par exemple, "actif", "inactif", "en attente de validation").


    def __str__(self):
        return self.name


class BlogAdministrateur(models.Model):
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE, null=True,related_name='admin')
    user = models.ManyToManyField(MyUser,  related_name='blog')
    niveau_admin = models.IntegerField()



class ProfileBlog(models.Model):
    contact_telephone = models.CharField(max_length=25, blank=True, null=True)
    longetude = models.IntegerField(null=True, blank=True)
    latitude = models.IntegerField(null=True, blank=True)
    blog = models.OneToOneField(Blog, related_name='profil', on_delete=models.CASCADE, null=True)
    ville = models.CharField(max_length=30,null=True, blank=True)
    pays = models.CharField(max_length=30,null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    site_web = models.URLField(null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    type_salon = models.CharField(max_length=100,  blank=True, default='femme')
    commune = models.CharField(max_length=30,null=True)
    adresse = models.CharField(max_length=255,null=True, blank=True)

class ImageProfilBlog(BaseImage):
    image = models.ImageField(upload_to=upload_to_unique_uuid_image, null=True) 
    blog = models.OneToOneField(Blog, related_name='image',on_delete=models.CASCADE, null=True)
    video = models.FileField(upload_to=upload_to_unique_uuid, null=True) 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'blog/images_profile/'
class Service(models.Model):
    wifi = models.BooleanField(blank=True,null=False,default=False)
    service_traiteur = models.BooleanField(blank=True,null=False,default=False)
    livraison = models.BooleanField(blank=True,null=False,default=False)
    parking = models.BooleanField(blank=True,null=False,default=False)
    evenement = models.BooleanField(blank=True,null=False,default=False)
    service_domicile = models.BooleanField(blank=True,null=False,default=False)
    emporter =models.BooleanField(blank=True,null=False,default=False)
    manucure_pedicure = models.BooleanField(blank=True,null=False,default=False)
    maquillage = models.BooleanField(blank=True,null=False,default=False)
    coifure_evenement = models.BooleanField(blank=True,null=False,default=False)
    vente_article = models.BooleanField(blank=True,null=False,default=False)
    booking = models.BooleanField(blank=True,null=False,default=True)
    conseil_beaute = models.BooleanField(blank=True,null=False,default=False)
    
    
    blog = models.OneToOneField(Blog,related_name='services', on_delete=models.CASCADE, null=True)
    





class Employer(models.Model):
    full_name = models.CharField(max_length=255, blank=False, null=False,default='')
    date_naissance = models.DateField(null=True, blank=True)
    adresse = models.CharField(max_length=255, blank=True, null=True,db_default='')
    date_embauche = models.DateField(blank=True, null=True)
    fonction = models.CharField(max_length=25, null=True, blank=True)
    sexe = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=25,blank=True,null=True)#actif, innactif en conger revoyer demissionner
    telephone = models.CharField(max_length=25,blank=True,null=True)
    user = models.ForeignKey(MyUser, on_delete=models.SET_NULL,blank=True,null=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True)
    mail = models.EmailField(null=True,blank=True)
    devise =models.CharField(max_length=255, blank=True, null=True,db_default='$')



       

class Revenus(models.Model):
    montant = models.FloatField(null=True, blank=False)
    description = models.CharField(max_length=500, blank=True, null=True)

    date_revenu = models.DateField(null=True)
    """ex: "Ventes_nourriture", "Ventes_boissons", 
"Service_traiteur", "Pourboires"). """
    name  = models.CharField(max_length=25,default='')
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE,null=True, related_name='revenu')
    def __str__(self):
        return self.name+' '+ self.blog.name

class Depenses(models.Model):
    montant = models.FloatField(null=True, blank=False)
    date_depense = models.DateField(null=True)
    description = models.CharField(max_length=500,blank=True,null=True)
    
    name  = models.CharField(max_length=25,default='')
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE,null=True, related_name='depenses')
    
    def __str__(self):
        return self.name +' '+ self.blog.name
    

class Dettes(models.Model):
    montant = models.FloatField(null=True, blank=False)
    date_dettes = models.DateField(null=True,blank=True)
    description = models.CharField(max_length=1000,blank=True,null=True)
    datte_rembourssement =models.DateField(null=True,blank=True)
    
    name  = models.CharField(max_length=25,default='')
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE,null=True,related_name='dettes')
    
    def __str__(self):
        return self.name +' '+ self.blog.name
    
class Stock(models.Model):
    name_article = models.CharField(max_length=255)
    categorie = models.CharField(max_length=500, null=True, blank=True)
    quantite = models.IntegerField(null=True,blank=True)
    unite = models.CharField(max_length=20, null=True,blank=True)
    seuil_alert=models.IntegerField(null=True, blank=True)
    modify_at = models.DateField(auto_now=True)
    prixAchat = models.IntegerField(null=True, blank=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.name_article +' '+ self.blog.name

class Reservation(models.Model):
    description = models.CharField(max_length=1500, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_reservation = models.DateTimeField()
    status = models.CharField(max_length=50,blank=True, default='Attente')#attent , annuler, reporter,reussi
    message  = models.CharField(max_length=1500, null=True, blank=True)
    qr_resevation = models.ImageField(upload_to=BaseImage.upload_to_unique_uuid, null=True, blank=True)
    montant = models.IntegerField(null=True, blank=True)# nombre d'heure pourune anulation
    user = models.ForeignKey(MyUser,null=True, on_delete=models.SET_NULL, related_name='reservation',blank=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE,blank=True, null=True, related_name='reservation')
    full_name= models.CharField(max_length=255)
    phone = models.CharField(max_length=25, null=True, blank=True)
    mail = models.EmailField(null=True, blank=True)
    nbr_personne = models.IntegerField(null=True,blank=True)
    """ Montant obligatoire pour confirmer la reservation """
    From = models.CharField(max_length=10, default='blog', blank=True)
    code = models.CharField(max_length=10, null=True, blank=True)
    type_montant= models.CharField(max_length=10, null=True, blank=True,default='verser')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'image_qr/'

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

        self.qr_resevation.save('qr_code.png', img_file,save=False)

    

class ImageReservation(BaseImage):
    image = models.ImageField(upload_to=BaseImage.upload_to_unique_uuid, null=True)
    reservation = models.ForeignKey(Reservation, related_name='images',on_delete=models.CASCADE, null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'image_reservation/'


class Horaire(models.Model):
    blog = models.OneToOneField(Blog, on_delete=models.CASCADE, null=True)
    days = models.TextField()

    def set_days(self, details_dict):
        self.days = json.dumps(details_dict)

    def get_days(self):
        if self.days:
            return json.loads(self.days)
        return {}
    def save(self, *args, **kwargs):
        
        if isinstance(self.days, dict):
            self.days = json.dumps(self.days)
        super().save(*args, **kwargs)



class Politique_reservation(models.Model):
    delai_annulation_min = models.IntegerField(null=True, blank=True)# nombre d'heure pourune anulation
    delai_report_min = models.IntegerField(null=True, blank=True)# nombre d'heure pourune anulation
    remboursement = models.CharField(max_length=15, null=True,blank=True)
    """ 3 possibiliter rembourssement total, un pourcentage ou rien"""
    pourcentation_remboursement = models.IntegerField(null=True, blank=True)# nombre d'heure pourune anulation
    # Ex rembourser 60% du montant recus

    class Meta:
        abstract = True


# models.py
from django.db import models
from django.utils import timezone

class Employe(models.Model):
    """
    Modèle représentant un employé.
    """
    full_name = models.CharField(max_length=150, verbose_name="Nom complet")

    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"

class Presence(models.Model):
    """
    Modèle pour enregistrer les pointages de présence des employés.
    """
    employee = models.ForeignKey(
        Employe, 
        on_delete=models.CASCADE, 
        related_name='presences',
        verbose_name="Employé"
    )
    arrival_time = models.DateTimeField(verbose_name="Heure d'arrivée")
    is_present = models.BooleanField(default=True, verbose_name="Est présent")
    is_late = models.BooleanField(default=False, verbose_name="Est en retard")
    
    def __str__(self):
        return f"Présence de {self.employee.full_name} le {self.arrival_time.strftime('%d-%m-%Y')}"

    def save(self, *args, **kwargs):
        # Logique pour déterminer si l'employé est en retard
        # Vous pouvez ajuster cette heure en fonction de vos besoins
        heure_limite = timezone.localtime(self.arrival_time).replace(hour=8, minute=30, second=0, microsecond=0)
        
        if self.arrival_time > heure_limite:
            self.is_late = True
        else:
            self.is_late = False
            
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        ordering = ['-arrival_time']


class Catalogue(models.Model):
 
    name_service = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True,blank=True)
    price = models.FloatField()
    categorie = models.CharField(max_length=255, null=True,blank=True)
    devise = models.CharField(max_length=10,default='$')
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE,null=True,blank=True)

    image = models.ImageField(upload_to=BaseImage.upload_to_unique_uuid, null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'blog/catalogue_images' 
       