from django.urls import path, re_path, include
from . import views

urlpatterns = [
    
    re_path('listeRestaurant/', views.listeRestaurant,name='liste_restaurant'),
]
