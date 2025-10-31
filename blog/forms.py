from django import forms
from blog.models import *
import re


class FormulaireBlog(forms.ModelForm):

    class Meta:
        model = Blog
        fields = ('name','type_page')
        


class FormProfilBlog(forms.ModelForm):

    class Meta:
        model = ProfileBlog
        fields = ('contact_telephone','ville','pays','email','description','commune','adresse')

 
class FormImageProfilBlog(forms.ModelForm):

    class Meta:
        model = ImageProfilBlog
        fields = ('image','video')

class FormService(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('wifi','service_traiteur','livraison',
                  'parking','evenement','service_domicile','emporter','manucure_pedicure','maquillage',
                  'coifure_evenement','vente_article')
        

class FormDettes(forms.ModelForm):
    class Meta:
        model = Dettes
        fields = ('montant', 'description','date_dettes','datte_rembourssement' )
                  
class FormResrevation(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('description', 'date_reservation', 'montant','type_montant',
                    'phone', 'full_name','mail','message','nbr_personne')
        
   
            
class FormAddEmployer(forms.ModelForm):
    class Meta:
        model = Employer
        fields = ('date_naissance', 'adresse','date_embauche',
                   'fonction','sexe','telephone', 'full_name','mail','devise')


class FormRevenus(forms.ModelForm):
    class Meta:
        model = Revenus
        fields = ('montant', 'description', 'date_revenu', 'name',)
    
class FormDepenses(forms.ModelForm):
    class Meta:
        model = Depenses
        fields = ('montant', 'description', 'date_depense', 'name',)

class FormCatalogue(forms.ModelForm):
    class Meta:
        model = Catalogue
        fields = ('name_service','description','price','categorie','image','devise')

class FormStock(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ('name_article', 'categorie','quantite', 'unite','seuil_alert','prixAchat')
  