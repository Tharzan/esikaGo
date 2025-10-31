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
]