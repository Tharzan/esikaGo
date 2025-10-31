from django import forms
from .models import *
import datetime

class FormConnexion(forms.Form):
    numero_tel = forms.CharField(max_length=25)
    password = forms.CharField(max_length=25)

    
class FormPostProduit(forms.ModelForm):
    class Meta:
        model = PostProduit
        fields = ('name_service','description','price','image','devise')

class FormTraveaux(forms.ModelForm):
    mois = models.CharField(max_length=20)
    annee = models.CharField(max_length=20)
    class Meta:
        model = Reabilitation
        fields = ('date', 'description','budget','devise')

    
    def clean(self):
        cleaned_data = super(FormTraveaux, self).clean()
        mois = cleaned_data.get('mois')
        annee = cleaned_data.get('annee')

        if mois and annee:
            try:
                mois = int(mois) 
            except:
                raise forms.ValidationError('pas un  bon format du mois')
            try:
                annee = int(annee) 
            except:
                raise forms.ValidationError("pas un  bon format de l'année")
        else:
            raise forms.ValidationError('nom et prenom')
        date = datetime.date(annee,mois,1)
       
        self.cleaned_data['date'] = date
        return cleaned_data


