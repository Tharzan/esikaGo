from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from blog.forms import *
from blog.models import *
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
import qrcode
import json

@login_required
def createBlog(request):
    

    if request.method == 'POST':

        form = FormulaireBlog(request.POST)
        
        if form.is_valid():
            
            
            page = form.save()
            
            user=request.user
            request.session['id_page'] = page.id
            
            adminBlog = BlogAdministrateur.objects.create(blog=page, niveau_admin=1)
            adminBlog.user.add(user)
            
            adminBlog.save()
            
            
            return render(request,'blog/profil_blog.html',{'page': page})
        

            
        else:
            return render(request,'blog/createBlog_.html',  {'formError':True})
        
        
    
    else:
        form = FormulaireBlog()
        return render(request,'blog/createBlog_.html', locals())
    
@login_required
def editerBlog(request):
    if 'id_page' in request.session:

        id =  request.session['id_page']
        
        
    else:
        redirect('accueil')
    
    try:
        page = Blog.objects.get(id=int(id))
        request.session['id_blog'] = page.id
        
    except:
        return redirect('accueil')
    
    try:
        profile = ProfileBlog.objects.get(blog=page)
        has_profile = True
        
       
    except:
        has_profile = False
  
    services_disponibles = []
    
    try:
        
        service_instance = Service.objects.get(blog=page)
        
        
        # Dictionnaire pour la correspondance entre noms de champs et noms lisibles
        services_map = {
            'wifi': 'Wi-Fi',
            'service_traiteur': 'Service traiteur',
            'livraison': 'Livraison',
            'parking': 'Parking',
            'evenement': 'Événements',
            'service_domicile': 'Service à domicile',
            'emporter': 'À emporter',
            'manucure_pedicure': 'Manucure & Pédicure',
            'maquillage': 'Maquillage',
            'coifure_evenement': 'Coiffure événementielle',
            'vente_article': 'Vente d\'articles',
            'booking': 'Réservation en ligne',
            'conseil_beaute': 'Conseil beauté',
        }
        
        
        
        # On parcourt le dictionnaire pour vérifier la valeur de chaque champ
        for champ_modele, nom_lisible in services_map.items():
            # La fonction getattr() permet d'obtenir la valeur d'un champ
            # de manière dynamique en utilisant son nom sous forme de chaîne de caractères.
            if getattr(service_instance, champ_modele):
                services_disponibles.append(champ_modele)
        
        
    except:
        pass


    
    if page.type_page == 'restaurant':
        
        liste_service = {'wifi':'wifi','livraison':'Livraison à domicile',
        'service_traiteur':'Service traiteur','evenement': 'Événement personnel',
       'emporter': 'Nourriture à emporter','parking': 'Parking',
       'vente_article': 'Vente en ligne'}
        
    elif page.type_page == 'salon':

        liste_service = {'wifi':'wifi','livraison':'Livraison à domicile de produit',
    'parking': 'Parking', 'vente_article': 'Vente des produits','conseil_beaute': 'conseil de beauté',
    'coifure_evenement': 'coifure en groupe evenement', 'maquillage':'maquillage', 'manucure_pedicure':'manucure pedicure'}
        
    else:
        liste_service = {}
    
    if request.method == 'POST':
        

        form = FormProfilBlog(request.POST, request.FILES)
        if form.is_valid():
            
            if has_profile:
                profile.delete()

                profil = form.save(commit=False)
                profil.blog =  page
                
                profil.save()
                images_poste = ImageProfilBlog(blog=page)
                save = False
                for image in request.FILES.getlist('image'):
                    try:
                        ImageProfilBlog.objects.filter(blog=page).delete()

                    except:
                        pass
                    if image:
                        images_poste.image=image
                        save = True
                        
                for video in request.FILES.getlist('video'):
                    try:
                        ImageProfilBlog.objects.filter(blog=page).delete()

                    except:
                        pass
                    if video:
                        images_poste.video=video
                        save = True

                        
                if save:
                    images_poste.save()
            else:

                profil = form.save(commit=False)
                profil.blog =  page
                
                profil.save()
                images_poste = ImageProfilBlog(blog=page)
                save = False
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


            
            # ------ service de la page ---------

            service = FormService(request.POST)
            if service.is_valid():
                try:
                    service_set = Service.objects.filter(blog=page)
                    service_set.delete()
                    
                except:
                    return HttpResponse('rien')
               
                
                service = service.save(commit=False)
                service.blog = page
                
                service.save()
                
            else:
                pass
            return redirect(reverse('profil_blog', kwargs={'id': page.id}))
                
                
        else:
            return render(request,'blog/edite_profil_blog.html',{'page': page, 'formError':True, 'liste_service':liste_service,'service':services_disponibles})
        
        
    else:
        if has_profile:
            return render(request,'blog/edite_profil_blog.html',{'liste_service':liste_service, 'page': page,'profile':profile,'service':services_disponibles})
        else:
            return render(request,'blog/edite_profil_blog.html',{'page': page,'liste_service':liste_service, 'service':services_disponibles})
    



@login_required  
def blog(request, id):
    try:
        page = Blog.objects.get(id=int(id))
        request.session['id_page'] = page.id
        return render(request,'blog/blog.html', {'page': page})
       
    except:
        return redirect('accueil')


 
@login_required
def profil_blog(request,id):
    try:
        id = id
        page = Blog.objects.get(id=int(id))
        return render(request,'blog/profilBlog.html', {'page': page})
        
    except:
                       
        return redirect('accueil')
        

@login_required    
def gestion_blog(request):
    
    try:
        
        id = request.session['id_page']
        page = Blog.objects.get(id=int(id))
       
    
        
        return render(request,'blog/gestion_blog.html', {'page': page})
        
        
    except:
                       
        return redirect('accueil')
   
            
    



@login_required    
def presence(request):
    
    
    try:
        
        id = request.session['id_page']
        page = Blog.objects.get(id=int(id))
        #liste_employer = Employer.objects.filter(blog=page)
        
        return render(request,'blog/presence.html', {'page': page})
    except:
        return redirect('accueil')
    

@login_required    
def liste_employer(request):
    try:
        id = request.session['id_page']
        page = Blog.objects.get(id=int(id))
        liste_employer = Employer.objects.filter(blog=page)
        field_name = ['full_name','adresse','fonction','telephone','sexe','mail']
        # Créer une liste de dictionnaires
        data_employer = []
        
        for employer in liste_employer:
            
            employer_dict = {}
            # Boucle sur les champs du modèle de manière dynamique
            for field in field_name:
                
                field_value = getattr(employer, field)
                if field_value is None:
                    field_value = ''

                employer_dict[field] = field_value
            

            data_employer.append(employer_dict)
            nbr_femme = 0
            for employer in data_employer:
                if employer['sexe'] == 'femme':
                    nbr_femme = nbr_femme + 1
            data_statistique = {}
            
            total= int(len(data_employer))
            nbr_homme = total - nbr_femme

        # Convertir la liste de dictionnaires en JSON
        json_data = json.dumps(data_employer, indent=4,ensure_ascii=False)
        graphique = [nbr_homme, nbr_femme]
        
        data_statistique = json.dumps(graphique, indent=4,ensure_ascii=False)
        
      
        
        return render(request, 'blog/liste_employer.html',
 {'page': page,'data_statistique':data_statistique, 'employers': data_employer,'total':total, 'nbr_femme':nbr_femme, 'nbr_homme': nbr_homme})
    except:
        return render(request, 'blog/liste_employer.html',
 {'page': page, 'total':0, 'nbr_femme':0, 'nbr_homme': 0})
 

    

@login_required    
def reservation(request):
    b = str(request.session['id_page'])
    
    try:
        
        id = request.session['id_page']
        page = Blog.objects.get(id=int(id))
       
    
        if request.method == 'POST':
           
            form = FormResrevation(request.POST, request.FILES)
            if form.is_valid():
                
                instance = form.save()
                
                name = f"{uuid.uuid4().hex[:6]}"
                data = 'http://172.20.10.3:8000/viewReservation/' + name
                instance.image_qr(data)
                instance.blog = page
                
                instance.code = name
                instance = instance.save()
                url = 'blog/viewReservation/' + name
            
                return render(request,url)
        else:
            return render(request,'blog/reservation.html', {'page': page})
        
        
    except:
                       
        return redirect('accueil')
   
            
    
   
def vue_reservation(request, code):
    try:
        
        reservation = Reservation.objects.get(code=code)
        
        try:
            id = request.session['id_page']
            page = Blog.objects.get(id=int(id))
            return render(request,'blog/view_reservation.html', {'page': page,'reservation':reservation})
        
        except:
            return render(request,'blog/view_reservation.html', {'reservation': reservation})

    except:
        return redirect('accueil')

def dict_horaire(dictionnaire, key):
    value =  dictionnaire.get(key)

    return value 

@login_required     
def horaire(request, id):
    try:
        page = Blog.objects.get(id=int(id))

        if request.method == 'POST':
            dictionnaireDays = {}
            for jour in ['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche']:
                dictionnaireDays[jour] = dict_horaire(request.POST, jour)
            

            for jour in dictionnaireDays.keys():
               
                if dictionnaireDays[jour] == 'on':
                    key1 = jour + '_debut'
                    time_debut = request.POST.get(key1)
                    key2 = jour + '_fin'
                    time_fin = request.POST.get(key2)

                    dictionnaireDays[jour] = [time_debut,time_fin]
                else:
                    pass
            horaire = Horaire()
            horaire.set_days(dictionnaireDays)
            horaire.blog = page
            horaire.save()
            return render(request,'blog/horaire.html', {'page': page})
            
            

        else:
            return render(request,'blog/horaire.html', {'page': page})
    except:
        return redirect('accueil')

@login_required     
def add_employer(request):
    
    try:
        if 'id_page' in request.session:
            id = request.session['id_page']
        else:
            
            raise ValueError
        page = Blog.objects.get(id=int(id))
    
        if request.method == 'POST':
            
            form = FormAddEmployer(request.POST)
            if form.is_valid():
                
               
                employer = form.save() 
                employer.blog = page
                employer.save()
                return redirect('liste_employer') 
                
            else:
                return render(request,'blog/addEmployer_.html', {'formError':True, 'page': page})
   
           
        
        return render(request,'blog/addEmployer_.html', {'page': page})
    except:
               
        return redirect('accueil')


@login_required     
def catalogue(request,id=None):
    
    try:
        if 'id_page' in request.session:
            id = request.session['id_page']
        else:
            
            raise ValueError
        page = Blog.objects.get(id=int(id))
    
        if request.method == 'POST':
            
            pass
                
        else:
                return render(request,'blog/catalogue.html', {'formError':True, 'page': page})
   
           
        
        return render(request,'blog/catalogue.html', {'page': page})
    except:
               
        return redirect('accueil')


        
def stock(request):
    try:
        if 'id_page' in request.session:
            id = request.session['id_page']
        else:
            
            raise ValueError
        page = Blog.objects.get(id=int(id))

        if request.method == 'POST':
            form = FormStock(request.POST)
            if form.is_valid():
                instance = form.save()
                instance.blog = page
                instance.save()
                return redirect(reverse('blog',kwargs={'id':page.id}))
            else:
                return render(request,'blog/stock_produit.html', {'formError':True, 'page': page})
        return render(request,'blog/stock_produit.html', {'page': page})
    
    except:
        return redirect(reverse('accueil'))
def revenus(request):
    try:
        if 'id_page' in request.session:
            id = request.session['id_page']
        else:
            
            raise ValueError
        page = Blog.objects.get(id=int(id))

        if request.method == 'POST':
            form = FormRevenus(request.POST)
            
            if form.is_valid():
                
                instance = form.save(commit=False)
                instance.blog = page
                instance.save()
                return redirect('gestion_blog')
            else:
                return render(request,'blog/revenus.html', {'formError':True, 'page': page})
        return render(request,'blog/revenus.html', {'page': page})
    
    except:
        return redirect(reverse('accueil'))

def depenses(request):
    try:
        if 'id_page' in request.session:
            id = request.session['id_page']
        else:
            
            raise ValueError
        page = Blog.objects.get(id=int(id))

        if request.method == 'POST':
            form = FormDepenses(request.POST)
            if form.is_valid():
                instance = form.save()
                instance.blog = page
                instance.save()
                return redirect('gestion_blog')
            else:
                return render(request,'blog/revenus.html', {'formError':True, 'page': page})
            
        return render(request,'blog/depenses.html', {'page': page})
    
    except:
        return redirect(reverse('accueil'))
    

def dettes(request):
    try:
        
        if 'id_page' in request.session:
            id = request.session['id_page']
        else:
            
            raise ValueError
        page = Blog.objects.get(id=int(id))
        
        if request.method == 'POST':
            form = FormDettes(request.POST)
            
            if form.is_valid():
                
                instance = form.save(commit=False)
                instance.blog = page
                instance.save()
                return redirect('gestion_blog')
            else:
                return render(request,'blog/dettes.html', {'formError':True, 'page': page})
            
        
        return render(request,'blog/dettes.html', {'page': page})
    
    except:
        
        return redirect(reverse('accueil'))


@login_required     
def registermenu(request):
    try:
        
        if 'id_page' in request.session:
            id = request.session['id_page']
            page = Blog.objects.get(id=int(id))
            
        else:
            
            raise ValueError
        
        
        if request.method == 'POST':
            
            form = FormCatalogue(request.POST,request.FILES)
            
            
            if form.is_valid():
                  
                instance = form.save(commit=False)
                instance.blog = page
                instance.save()
                return redirect('catalogue')
            else:
                return render(request,'blog/registermenu.html', {'formError':True, 'page': page})
        return render(request,'blog/registermenu.html', {'page': page})
    
    except:
         return redirect(reverse('accueil'))


     