from django import forms
from my_user.models import *
import re

class FormulaireConnexion(forms.ModelForm):
    numero_validation = True
    class Meta:
        model = MyUser
        fields = ['numero_tel', 'first_name','last_name', 'email', 'password', 'email_authenticate','sexe']

    def clean(self):
        cleaned_data = super(FormulaireConnexion, self).clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        if first_name and last_name:
            cleaned_data['username'] = last_name + ' ' + first_name
        else:
            raise forms.ValidationError('nom et prenom')
        
        numero = self.cleaned_data['numero_tel']
        numero_regex = r'^0[89]{1}[0-9]{8}$'
        if re.fullmatch(numero_regex, numero):
            self.cleaned_data['numero_tel'] = numero
        else:
            self.cleaned_data['numero_tel'] = numero + '_'
            self.cleaned_data['email'] = numero
            self.cleaned_data['email_authenticate'] = True
        return cleaned_data



class FormProfilUser(forms.ModelForm):
    class Meta:
        model = ProfileUser
        fields = ('contact_telephone','email','date_naissance','commune','rue','numero_rue','description')

class FormImageProfil(forms.ModelForm):

    class Meta:
        model = ImageProfil
        fields = ('image','video')


class FormRevenus(forms.ModelForm):
    class Meta:
        model = Revenus
        fields = ('montant', 'description', 'date_revenu', 'name',)

class FormDettes(forms.ModelForm):
    class Meta:
        model = Dettes
        fields = ('montant', 'description','date_dettes','datte_rembourssement' )
    
class FormDepenses(forms.ModelForm):
    class Meta:
        model = Depenses
        fields = ('montant', 'description', 'date_depense', 'name',)

class FormSecurity(forms.ModelForm):
    class Meta:
        model = Secutity
        exclude = ('date_creation', 'date_modification','user','cle_publique')



        def clean_signature(self):
            cleaned_data = super(FormulaireConnexion, self).clean()
            first_name = cleaned_data.get('signature')
            
            return cleaned_data
        


class DocumentUploadForm(forms.Form):
    """
    Formulaire utilisé pour uploader un document PDF et spécifier son type 
    avant le processus de signature et d'ancrage.
    """
    
    document_file = forms.FileField(
        label='Sélectionner le Document PDF',
        help_text='Seuls les fichiers PDF sont acceptés.',
        # Optionnel: Vous pouvez ajouter une validation personnalisée ici
    )
    
    type_document = forms.CharField(
        label='Type de Document',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Contrat de Bail, Facture, Quittance de Loyer'})
    )

    def clean_document_file(self):
        """Validation personnalisée pour s'assurer que le fichier est bien un PDF."""
        data = self.cleaned_data['document_file']
        
        # Vérification simple du type de fichier
        if not data.name.lower().endswith('.pdf'):
            raise forms.ValidationError("Le fichier doit être au format PDF.")
        
        # Vous pouvez ajouter ici d'autres validations (taille, etc.)
        
        return data

# Note: Assurez-vous d'importer ce formulaire dans votre fichier views.py :
# from .forms import DocumentUploadForm

