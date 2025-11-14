from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required

from my_user.models import MyUser
from blog.models import  Blog,BlogAdministrateur
from app_general.forms import FormConnexion
import re
from .forms import *

from hedera import (
    Client, PrivateKey, AccountId, TopicId,
    TopicMessageQuery
)
import os
import hashlib
from dotenv import load_dotenv
import datetime




def index(request):
    liste = [1,2,3,4]
    
    return render(request, 'app_general/index.html', locals())

def logout_view(request):
    logout(request)
    return redirect('accueil')

def about(request):
    
    return render(request, 'app_general/Apropos.html', locals())


def login_view(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        form = FormConnexion(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            numero = form.cleaned_data['numero_tel']

            if re.search(r'[a-zA-Z]', numero):
                numero = numero + '_'
            user = authenticate(password=password,numero_tel=numero)
            if user:
                login(request, user)
                return redirect('accueil_user')
                
            else:
                render(request,'app_general/login.html')

    else:
    
        return render(request,'app_general/login.html')

@login_required
def accueil(request):
        
        today = datetime.date.today()
        day = today.strftime('%d')
        month = today.strftime('%b').upper()

        date = str(month) + ' ' + str(day)

        user = request.user
        request.session['has_page'] = False
        liste_blog= list()
        try:
            administre  = BlogAdministrateur.objects.filter(user=user)
            for objet in administre:
                liste_blog.append(objet.blog)
            request.session['has_page']  = True
            

        except:
            has_blog = False
        return render(request, 'app_general/accueil.html', locals())



@login_required
def message(request):
        
        today = datetime.date.today()
        day = today.strftime('%d')
        month = today.strftime('%b').upper()

        date = str(month) + ' ' + str(day)

        user = request.user
        request.session['has_page'] = False
        liste_blog= list()
        try:
            administre  = BlogAdministrateur.objects.filter(user=user)
            for objet in administre:
                liste_blog.append(objet.blog)
            request.session['has_page']  = True
            

        except:
            has_blog = False
        return render(request, 'app_general/message.html', locals())



@login_required
def traveaux(request,page=None):
        
        if page=='page':
            if 'id_page' in request.session:
                id = request.session['id_page']
                page = Blog.objects.get(id=int(id))
                post = 'page'
            else:
                raise ValueError
        elif page is None:
            post = 'user'   
        else:
            
            raise ValueError
        
        
        if request.method == 'POST':
            
            form = FormTraveaux(request.POST)
            
            
            if form.is_valid():
                return HttpResponse("bbbbb")
                  
                instance = form.save(commit=False)
                if post == 'page':
                    instance.blog = page
                    instance.save()
                    return redirect('traveaux_page')
                else:
                    instance.user = request.user
                    instance.save()
                    return redirect(reverse('traveaux', kwargs={'user': request.user.id}))
            else:
                return render(request,'app_general/traveaux.html', {'formError':True, 'page': page})
  
        else:
            return render(request, 'app_general/traveaux.html', {'page': page})
    
    


      


@login_required     
def saveproduit(request,page=None):
    
        
        if page=='page':
            if 'id_page' in request.session:
                id = request.session['id_page']
                page = Blog.objects.get(id=int(id))
                post = 'page'
            else:
                raise ValueError
        elif page is None:
            post = 'user'   
        else:
            
            raise ValueError
        
        
        if request.method == 'POST':
            
            form = FormPostProduit(request.POST,request.FILES)
            
            
            if form.is_valid():
                  
                instance = form.save(commit=False)
                if post == 'page':
                    instance.blog = page
                    instance.save()
                    return redirect('catalogue')
                else:
                    instance.user = request.user
                    instance.save()
                    return redirect(reverse('profil_user', kwargs={'user': request.user.id}))
            else:
                return render(request,'app_general/saveproduit.html', {'formError':True, 'page': page})
        return render(request, 'app_general/saveproduit.html', {'page': page})
    
def calculate_file_hash(filename):
    hasher = hashlib.sha256()
    try:
        with open(filename, 'rb') as file:
            buf = file.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except FileNotFoundError:
        print(f"❌ Erreur: Le fichier '{filename}' n'a pas été trouvé.")
        return None

def verify(request, code=None):
   

    HCS_TOPIC_ID = TopicId.fromString("0.0.7132193") 
    DOCUMENT_FILE_NAME = "document.pdf"
    PROOF_FILE_NAME = "proofs.txt" 

    if request.method == 'POST':

        # 1. Configuration du Client (inchangée)
        OPERATOR_ID = AccountId.fromString(os.environ["MY_ACCOUNT_ID"])
        OPERATOR_KEY = PrivateKey.fromString(os.environ["MY_PRIVATE_KEY"])
        client = Client.forTestnet()
        client.setOperator(OPERATOR_ID, OPERATOR_KEY)

        # 2. Calcul du HASH SHA-256 du document actuel (inchangé)


        current_document_hash = calculate_file_hash(DOCUMENT_FILE_NAME)

        if not current_document_hash:
            exit()
            
        # 3. 🚨 Récupération du HASH ANCRÉ à partir du fichier
        last_anchored_hash = None
        anchored_time = None
        try:
            with open(PROOF_FILE_NAME, "r") as f:
                # On lit toutes les lignes et on prend la dernière pour l'exemple
                lines = f.readlines()
                if lines:
                    # La dernière ligne contient: consensus_time,hash,transaction_id
                    last_line = lines[-1].strip()
                    parts = last_line.split(',')
                    anchored_time = parts[0]
                    last_anchored_hash = parts[1]
                else:
                    print(f"❌ Erreur: Le fichier '{PROOF_FILE_NAME}' est vide. Veuillez d'abord envoyer un hash.")
                    exit()
        except FileNotFoundError:
            print(f"❌ Erreur: Le fichier '{PROOF_FILE_NAME}' n'existe pas. Veuillez d'abord exécuter send_hcs_hash.py.")
            exit()

        # 4. Comparaison des Hashs
        print(f"Document vérifié par rapport à la preuve enregistrée à : {anchored_time}")
        print("\n---------------------------------------")
        print(f"HASH ANCRÉ (Hedera) : {last_anchored_hash}")
        print(f"HASH ACTUEL (Fichier) : {current_document_hash}")
        print("---------------------------------------")

        if current_document_hash == last_anchored_hash:
            print("✅ VÉRIFICATION RÉUSSIE : L'empreinte numérique du document est INTACTE.")
            print("   Le document est PROUVÉ comme étant celui ancré sur Hedera à la date du Consensus Time.")
        else:
            print("❌ ÉCHEC DE LA VÉRIFICATION : Le document a été MODIFIÉ (ou le mauvais fichier a été vérifié).")
