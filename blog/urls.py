from django.urls import path, re_path, include
from . import views


urlpatterns = [
    re_path('createBlog/', views.createBlog,name='create_blog'),
     re_path(r'^editerBlog/$', views.editerBlog,name='edite_blog'),
      re_path(r'blog/(?P<id>\d+)/$', views.blog,name='blog'),
    re_path(r'profileBlog/(?P<id>\d+)/$', views.profil_blog,name='profil_blog'),
    re_path(r'^reservation/$', views.reservation, name='reservation'),
     re_path(r'^horaire/(?P<id>\d+)/$', views.horaire, name='horaire'),
     re_path(r'^addEmployer/$', views.add_employer, name='add_employer'),
     re_path(r'^stock/$', views.stock, name='stock'),
     re_path(r'^revenus/$', views.revenus, name='revenus'),
     re_path(r'^depenses/$', views.depenses, name='depenses'),
     re_path(r'^gestionBlog/$', views.gestion_blog, name='gestion_blog'),
     re_path(r'^presence/$', views.presence, name='presence'),
    re_path(r'^liste_employer/$', views.liste_employer, name='liste_employer'),
    re_path(r'^dettes_blog/$', views.dettes, name='dette_blog'),
    re_path(r'^catalogue/$', views.catalogue, name='catalogue'),
     re_path(r'^catalogue/$', views.catalogue, name='catalogue'),
      path('catalogue/<int:id>/', views.catalogue, name='catalogue'),
    path('createcatalogue/', views.registermenu, name='createcatalogue'),

     re_path(r'^viewReservation/(?P<code>[a-zA-Z0-9]{6})/$', views.vue_reservation, name='view_reservation'),
]