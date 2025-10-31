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
    
    


        user = request.user
        request.session['has_page'] = False
        
        return render(request, 'app_general/traveaux.html', locals())



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
    
  