from django.urls import path, re_path, include
from . import views

urlpatterns = [
    
    re_path('accueil/', views.index,name='accueil'),
    re_path('deconnection/', views.logout_view,name='logout'),
    re_path(r'accueil_user/$', views.accueil,name='accueil_user'),
    re_path(r'accueil_user/$', views.accueil,name='accueil_user'),
    re_path(r'save_produit/$', views.saveproduit,name='saveproduit'),
    re_path(r'save_produit/(?P<page>[a-z]{4})$', views.saveproduit,name='saveproduit_page'),
   re_path(r'apropos/$', views.about,name='about'),
    re_path(r'connexion/$', views.login_view,name='login'),
    re_path(r'traveaux/$', views.traveaux,name='traveaux'),
    re_path(r'traveaux/(?P<page>[a-z]{4})$', views.traveaux,name='traveaux_page'),
]
