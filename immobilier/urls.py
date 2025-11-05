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

    # URL qui sera appelée APRÈS la soumission du formulaire de paiement
    # C'est la vue qui génère le PDF et l'enregistre dans la base de données
    re_path('quittance/enregistrer/(?P<id>.+)/$', 
         views.enregistrer_quittance, 
         name='enregistrer_quittance'), # <-- C'est le nom que vous utilisez dans le 'redirect'
    
    # URL de confirmation après l'enregistrement
    re_path('quittance/succes/(?P<id>.+)/$', 
         views.succes_enregistrement_quittance, 
         name='succes_enregistrement_quittance'), # <-- Cette vue doit être créée
    
    # ... (Autres URLs de votre application) ...
]