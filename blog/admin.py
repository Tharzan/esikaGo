from django.contrib import admin

from blog.models import *

class BlogAdmin(admin.ModelAdmin):
    list_display = ('id','name',)
class ProfilBlogAdmin(admin.ModelAdmin):
    list_display = ('blog__id','contact_telephone','commune','ville','pays','email')

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id','code','full_name','description','date_creation','date_modification',
                    'date_reservation'
                 ,'status','qr_resevation','montant','type_montant','From','user','blog',)

class EmployerAdmin(admin.ModelAdmin):
    list_display = ('id','full_name','blog', 'user','date_naissance', 'adresse','date_embauche',
                   'fonction','sexe','telephone','mail')
    

class HoraireAdmin(admin.ModelAdmin):
    list_display = ('blog','days')
admin.site.register(Blog, BlogAdmin)
admin.site.register(ProfileBlog, ProfilBlogAdmin)
admin.site.register(Service)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Employer, EmployerAdmin)
admin.site.register(Horaire, HoraireAdmin)
admin.site.register(Stock)
admin.site.register(Revenus)
admin.site.register(Depenses)
