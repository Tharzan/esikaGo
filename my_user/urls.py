from django.urls import path, re_path, include
from . import views
from my_user.views import UpdateProfile


urlpatterns = [
    re_path('createUser/', views.createUser,name='create_user'),
    re_path(r'^editerUser/$', views.editerUser,name='edite_user'),
     re_path(r'profileUser/(?P<user>\d+)/$', views.profil_user,name='profil_user'),
     re_path(r'myGestion/$', views.gestion,name='gestion_user'),
       re_path(r'UpdateprofileUser/(?P<pk>\d+)/$',UpdateProfile.as_view() ,name='update_profil_user'),
    re_path(r'^revenusUser/$', views.revenus, name='revenus_user'),
    re_path(r'^dettes/$', views.dettes, name='dettes'),
    re_path(r'^depensesUser/$', views.depenses, name='depenses_user'),
    re_path(r'^security/$', views.security, name='security'),
    re_path(r'^succes/$', views.succes_security_view, name='succes_security_rl'),
    re_path(r'^document/$', views.document_view, name='document'),

    re_path('security/download/', views.download_security_files, name='download_security_files'),
    # Le chemin de succès après téléchargement (succes_security_url) doit aussi exister

    # 1. URL pour afficher le formulaire d'upload et traiter la signature/ancrage
    # Nommé 'sign_and_anchor_document' comme utilisé dans le template HTML
    path('signDocument/', views.sign_and_anchor_document, name='sign_and_anchor_document'),
    
    # 2. URL pour la vérification du document via le QR code
    # <str:code> permet de capturer l'UUID généré dans l'URL (ex: /authentify/a1b2c3d4...)
    path('authentify/<str:code>/', views.authentify_document, name='authentify_document'),
    
    # URL pour afficher les détails du document signé après l'enregistrement
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
]
