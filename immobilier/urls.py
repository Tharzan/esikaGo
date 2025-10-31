from django.urls import path, re_path, include
from . import views

urlpatterns = [
    re_path('postMaison/', views.post_maison, name='post_maison'),
    re_path('listeMaison/', views.listeMaison, name='liste_maison'),
    re_path('detailMaison/', views.detailMaison, name='detail_maison'),
    re_path('saveProperty/', views.save_property, name='save_property'),
    re_path(r'historique/(?P<id>.+)/$', views.historique_maison, name='historique_maison'),
    re_path('bien_immobilier/', views.bien_immobilier, name='bien_immobilier'),
    re_path(r'^viewQuittance/(?P<id>.+)/$', views.view_quittance, name='view_quittance'),
]