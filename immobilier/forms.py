from django import forms
from immobilier.models import *

class FormulairePostMaison(forms.ModelForm):
    
    class Meta:
        
        model = PostMaison
        fields = ('pays', 'ville',  'commune', 'type_bien','nombre_chambre', 'nombre_piece', 
        'nombre_douche', 'description','price')

class FormSave_property(forms.ModelForm):
    class Meta:
        model = SaveProperty

        fields = ('type_bien', 'adresse','statut',
                   'montant', 'id_maison','nom_complet_occupant','tel_occupant', 'date_entrer',
                     'garantie','contratBail') 
        
class FormLoyer(forms.ModelForm):
    class Meta:
        model = Loyer
        fields = ('montant','date_payement','mois','observation','annee')