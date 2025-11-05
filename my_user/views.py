from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from my_user.forms import *
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from blog.models import  Blog,BlogAdministrateur
from django.views.generic import UpdateView
from core.models import generer_cles_et_certificat,process_and_save_signature
from django.conf import settings

from django.contrib import messages
from pathlib import Path
from django.core.files import File
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from django.http import StreamingHttpResponse , HttpResponseNotFound
import os
import time 

from django.core.files.base import ContentFile

# Imports requis pour le traitement des fichiers et clés
import os
import uuid
import base64 

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, FileResponse, Http404
from django.core.files import File
from django.core.files.base import ContentFile
from pathlib import Path


@login_required(login_url='login')
def security(request):
    
    user = request.user
    liste_blog = []
    
    # 1. Récupération des blogs (logique initiale)
    try:
        administre = BlogAdministrateur.objects.filter(user=user)
        for objet in administre:
            liste_blog.append(objet.blog)
    except Exception as e:
         
        pass 
    
    # --- Traitement POST ---
    if request.method == 'POST':
        form = FormSecurity(request.POST, request.FILES) 
        password = request.POST.get('password')
        
        signature_file_object = request.FILES.get('signature') 
        base64_image_data = request.POST.get('verification_faciale')
        verification_faciale_file = None 
        
        

        
        if form.is_valid():
            # Gestion du cas 'profil_existe_deja' (CORRIGÉ: utilise 'security' comme related_name)
            if hasattr(request.user, 'security'):
                security = request.security
                # En production on va le supprimer mais on met dans l'historique avant
                security.delete() 
                
                
            # --- VÉRIFICATIONS MANUELLES et PRÉ-TRAITEMENTS ---
            
            if not signature_file_object:
                messages.error(request,'signature', "La photo de votre signature est manquante.")
                return render(request, 'MyUser/security.html', {'liste_blog': liste_blog})
            
            if not base64_image_data:
                messages.error(request,'verification_faciale', "La photo de vérification faciale est manquante.")
                return render(request, 'MyUser/security.html', {'liste_blog': liste_blog})
            
            # Décodage Base64
            try:
                if 'base64,' in base64_image_data:
                    format, imgstr = base64_image_data.split(';base64,') 
                    ext = format.split('/')[-1]
                else:
                    raise ValueError("Format Base64 invalide pour l'image faciale.")
                
                file_name = f'{user.username}_face_{uuid.uuid4()}.{ext}'
                verification_faciale_file = ContentFile(base64.b64decode(imgstr), name=file_name)
                
            except Exception as e:
                messages.error(request,'verification_faciale', f"Erreur lors du décodage de l'image faciale: {e}")
                return render(request, 'MyUser/security.html', { 'liste_blog': liste_blog})
            
            
            # --- 1. TRAITEMENT DE LA SIGNATURE (OpenCV) ---
            temp_path = None
            final_signature_abs_path = None
            
            try:
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
                os.makedirs(temp_dir, exist_ok=True)
                temp_filename = f"temp_{uuid.uuid4()}_{signature_file_object.name}"
                temp_path = os.path.join(temp_dir, temp_filename)
                
                with open(temp_path, 'wb+') as destination:
                    for chunk in signature_file_object.chunks():
                        destination.write(chunk)
                
                # final_signature_abs_path est le chemin ABSOLU du fichier traité
                final_signature_abs_path = process_and_save_signature(temp_path)
                
            except Exception as e:
                messages.error(request,'signature', f"Erreur lors du traitement de la signature : {e}")
                return render(request, 'MyUser/security.html', { 'liste_blog': liste_blog})
            
            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

            
            # --- 2. GÉNÉRATION DE CLÉS ---
            try:
                # cle_privee_chemin et certificat_cle_publique sont les chemins ABSOLUS des fichiers générés
                cle_privee_chemin, certificat_cle_publique = generer_cles_et_certificat(
                    request.user.username, 
                    password
                )
            except Exception as e:
                messages.error(request, f"Erreur de génération de clés : {e}")
                if final_signature_abs_path and os.path.exists(final_signature_abs_path):
                    os.remove(final_signature_abs_path)
                return render(request, 'MyUser/security.html', {'liste_blog': liste_blog})
            
            
            # --- 3. PRÉPARATION ET SAUVEGARDE FINALE DANS LA DB ---
            
            security_instance = form.save(commit=False)
            security_instance.user = request.user
            
            try:
                # 1. Sauvegarde de la VÉRIFICATION FACIALE (ImageField)
                security_instance.verification_faciale.save(
                    verification_faciale_file.name, 
                    verification_faciale_file, 
                    save=False
                )
                
                # 2. Sauvegarde de la SIGNATURE (ImageField)
                media_root_path = Path(settings.MEDIA_ROOT)
                final_path = Path(final_signature_abs_path) 
                signature_relative_path = final_path.relative_to(media_root_path).as_posix()
                
                with open(final_signature_abs_path, 'rb') as f:
                    file_object = File(f)
                    security_instance.signature.save(signature_relative_path, file_object, save=False)
                
                # 3. Sauvegarde de la CLÉ PUBLIQUE (FileField)
                certificat_path_obj = Path(certificat_cle_publique)
                certificat_relative_path = certificat_path_obj.relative_to(media_root_path).as_posix()
                
                with open(certificat_cle_publique, 'rb') as f_cert:
                    cert_file_object = File(f_cert)
                    security_instance.cle_publique.save(certificat_relative_path, cert_file_object, save=False)

                # 4. Sauvegarde finale de l'instance complète
                security_instance.save() 
                
                # Nettoyage de la signature traitée (déjà copiée)
                if os.path.exists(final_signature_abs_path):
                    os.remove(final_signature_abs_path) 

                # 5. Préparation de la redirection pour le téléchargement de la clé PRIVÉE
                request.session['cle_privee_a_telecharger'] = cle_privee_chemin
                request.session['certificat_a_supprimer'] = certificat_cle_publique # Sera supprimé par la vue suivante
                
                return redirect('succes_security_rl')
                
                
            except Exception as e:
                return HttpResponse('ivGGi')
                return redirect('succes_security_url') 
                # Gestion des erreurs de sauvegarde/chemin
                # Nettoyage d'urgence des clés non liées à l'instance
                if final_signature_abs_path and os.path.exists(final_signature_abs_path): os.remove(final_signature_abs_path)
                if certificat_cle_publique and os.path.exists(certificat_cle_publique): os.remove(certificat_cle_publique)
                if cle_privee_chemin and os.path.exists(cle_privee_chemin): os.remove(cle_privee_chemin)
                
                form.add_error(None, f"Erreur critique de sauvegarde finale: {e}")
                return render(request, 'MyUser/security.html', {'form': form, 'liste_blog': liste_blog})
            
        else:
            return render(request, 'MyUser/security.html', {'form': form, 'liste_blog': liste_blog})

    # --- Traitement GET ---
    else:
        form = FormSecurity()
        return render(request, 'MyUser/security.html', {
            'form': form, 
            'liste_blog': liste_blog,
            'revenu_user': True ,

        })


def document_view(request):
    user = request.user
    liste_blog = []
    if hasattr(request.user, 'security'): 
            has_security = True
    else:
            has_security = False
    
    # 1. Récupération des blogs (logique initiale)
    try:
        administre = BlogAdministrateur.objects.filter(user=user)
        for objet in administre:
            liste_blog.append(objet.blog)
    except Exception as e:
        
        pass 
    return render(request, 'MyUser/document.html', {'liste_blog': liste_blog,'has_security': has_security  })


@login_required(login_url='login')
def succes_security_view(request):

    show_download_button = 'cle_privee_a_telecharger' in request.session
    
    context = {
        'show_download_button': show_download_button,
    }
    
    return render(request, 'MyUser/succes_security.html', context)


@login_required(login_url='login')
def download_security_files(request):
    
    cle_privee_path = request.session.get('cle_privee_a_telecharger')
    certificat_path = request.session.get('certificat_a_supprimer')
    
    # 1. Nettoyage immédiat de la session
    # Empêche le re-téléchargement si l'utilisateur clique plusieurs fois.
    if 'cle_privee_a_telecharger' in request.session:
        del request.session['cle_privee_a_telecharger']
    if 'certificat_a_supprimer' in request.session:
        # Suppression du certificat public du disque immédiatement
        if certificat_path and os.path.exists(certificat_path):
            os.remove(certificat_path)
            
    # 2. Vérification d'existence (Fichier manquant / Déjà téléchargé)
    if not cle_privee_path or not os.path.exists(cle_privee_path):
        # Si le fichier est déjà parti, on répond par une erreur 404
        return HttpResponseNotFound("Le fichier de clé est introuvable ou a déjà été téléchargé.") 
        
    # --- Fonction Génératrice pour le Streaming et le Nettoyage ---
    def file_iterator(file_path):
        """Lit le fichier par morceaux et le supprime APRES la lecture complète."""
        f = None
        try:
            f = open(file_path, 'rb')
            
            # Streaming du fichier
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk
        finally:
            # 🚨 Bloc de Nettoyage Sécurisé (Exécuté après l'envoi du dernier morceau)
            if f:
                f.close() # Fermeture du handle pour libérer le verrou Windows
                
            time.sleep(0.5) # Délai pour l'OS
            
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"INFO: Clé privée SUPPRIMÉE via StreamingHttpResponse: {file_path}")
            except Exception as e:
                print(f"ALERTE MAJEURE: Erreur de suppression de la clé: {e}")

    # 3. Création de la réponse StreamingHttpResponse
    try:
        response = StreamingHttpResponse(
            file_iterator(cle_privee_path), 
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(cle_privee_path)}"'
        response['Content-Length'] = os.path.getsize(cle_privee_path)
        
        # ✅ Renvoyer la réponse de TÉLÉCHARGEMENT (pas de redirection ici)
        return response 
        
    except Exception as e:
        # Gérer l'échec de lecture/téléchargement (avant le streaming)
        print(f"ERREUR TÉLÉCHARGEMENT: {e}")
        if os.path.exists(cle_privee_path):
            os.remove(cle_privee_path)
        
        # Retourner à la page de succès pour informer l'utilisateur de l'échec
        return redirect('succes_security_url')


def createUser(request):
    
    if request.method == 'POST':

        form = FormulaireConnexion(request.POST)
        
        if form.is_valid():
            nom = form.cleaned_data['username']
            numero = form.cleaned_data['numero_tel']
            password = form.cleaned_data['password']
            user = form.save()
            user.username = nom
            user.save()
            login(request,user)
            return redirect(reverse('profil_user',kwargs={'user': request.user.id}))
            
            
        else:
            #return HttpResponse('ivaliddd')
            return render(request, 'MyUser/createUser.html')
        
    else:
        form =FormulaireConnexion()
    return render(request, 'MyUser/createUser.html', locals())



@login_required(login_url='login')
def editerUser(request):
    profile_instance= {}
    try:
        id = request.user.id
        my_user = MyUser.objects.get(id=int(id))
        
    except:
        return redirect('accueil')
    try:
        profile = ProfileUser.objects.get(user=my_user)
        has_profile = True
        field_name = ['contact_telephone','email','date_naissance','commune','rue',
                      'numero_rue','description']
        
        for field in field_name:
            field_value = getattr(profile, field)     
            if field_value is None:
                field_value = ''
            profile_instance[field] = field_value
    except:
        
        has_profile = False
    
    if request.method == 'POST':
        form = FormProfilUser(request.POST, request.FILES)
        save = False
        if form.is_valid():
            if has_profile:
                profile.delete()

            profil_save = form.save(commit=False)
            profil_save.user =  my_user
            profil_save.save()
            images_poste = ImageProfil(user=my_user)
            for image in request.FILES.getlist('image'):
                if image:
                    images_poste.image=image
                    save = True
                    
            for video in request.FILES.getlist('video'):
                if video:
                    images_poste.video=video
                    save = True
            if save:
                    
                images_poste.save()
            return redirect(reverse('profil_user', kwargs={'user': request.user.id}))
            
            
                
        else:
            
            formError = True
            form = FormProfilUser
            return render(request,'MyUser/edite_profil_user.html',{'form':form, 'profile':profile_instance})

            
    else:
        form = FormProfilUser
        return render(request,'MyUser/edite_profil_user.html',{'form':form, 'profile':profile_instance})

    
def profil_user(request, user):
    if int(user) == request.user.id:
        user = request.user
        
        has_blog = False
        liste_blog = list()
       
        try:
            administre  = BlogAdministrateur.objects.filter(user=user)
            for objet in administre:
                liste_blog.append(objet.blog)
            has_blog = True
            

        except:
            has_blog = False

        try:
            profile = user.profile
            has_profile = True
        except:
            has_profile = False

        try:
            picture = user.image
            
            has_picture = True
        except:
            has_picture = False

        return render(request,'MyUser/profil_user.html', locals())
    else:
        try:
            user = MyUser.objects.get(id=int(user))
            
            return render(request,'MyUser/profil_user.html', locals())
                
        except:
            return redirect('accueil')

class UpdateProfile(UpdateView):
    template_name = 'MyUser/edite_profil_user.html'
    model = ProfileUser
    form_class = FormProfilUser
    success_url = reverse_lazy('profil_user')

def updateProfile(form,list_keys,object):
    for key in list_keys:
        valeur = form.get(key)
        if valeur:
            object  = valeur

    return object


@login_required(login_url='login')
def gestion(request):


        user = request.user
        
        liste_blog= list()
        has_blog = True
        try:
            administre  = BlogAdministrateur.objects.filter(user=user)
            for objet in administre:
                liste_blog.append(objet.blog)
                
            

        except:
            has_blog = False
        return render(request, 'MyUser/gestion_user.html', locals())

@login_required(login_url='login')
def revenus(request):
    user = request.user
    liste_blog= list()
    has_blog = True
    try:
        administre  = BlogAdministrateur.objects.filter(user=user)
        for objet in administre:
            liste_blog.append(objet.blog)
                
    except:
        has_blog = False

    if request.method == 'POST':
            form = FormRevenus(request.POST)
            
            if form.is_valid():
                
                instance = form.save(commit=False)
                instance.user = user
                instance.save()
                return redirect('gestion_user')
            else:
                return render(request,'MyUser/revenu.html', {'formError':True, 'liste_blog': liste_blog})
        

    return render(request,'MyUser/revenu.html', {'liste_blog': liste_blog,'revenu_user':True})
    
   
@login_required(login_url='login')
def depenses(request):

    user = request.user
    liste_blog= list()
    has_blog = True
    try:
        administre  = BlogAdministrateur.objects.filter(user=user)
        for objet in administre:
            liste_blog.append(objet.blog)
                
    except:
        has_blog = False
    

    if request.method == 'POST':
        form = FormDepenses(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = user
            instance.save()
            return redirect('gestion_user')
        else:
            return render(request,'MyUser/depenses.html', {'formError':True, 'liste_blog': liste_blog})
        

            
    return render(request,'MyUser/depenses.html', {'liste_blog': liste_blog})
    


@login_required(login_url='login')
def dettes(request):
    user = request.user
    liste_blog= list()
    has_blog = True
    try:
        administre  = BlogAdministrateur.objects.filter(user=user)
        for objet in administre:
            liste_blog.append(objet.blog)
                
    except:
        has_blog = False

    if request.method == 'POST':
            form = FormDettes(request.POST)
            
            if form.is_valid():
                
                instance = form.save(commit=False)
                instance.user = user
                instance.save()
                return redirect('gestion_user')
            else:
                return render(request,'MyUser/dettes.html', {'formError':True, 'liste_blog': liste_blog})
        

    return render(request,'MyUser/dettes.html', {'liste_blog': liste_blog,'revenu_user':True})
