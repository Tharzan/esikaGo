from django.contrib import admin

from my_user.models import *

class MyUserAdmin(admin.ModelAdmin):
    list_display = ('id','username', 'numero_tel', 'is_superuser','email', 'email_authenticate', 'last_name','first_name','sexe')


class ImageProfilAdmin(admin.ModelAdmin):
    list_display = ('id','image','video','user')

class ProfileUserAdmin(admin.ModelAdmin):
    list_display = ('id','contact_telephone','user','date_naissance','commune','rue','numero_rue')
     

admin.site.register(MyUser,MyUserAdmin)
admin.site.register(ImageProfil,ImageProfilAdmin)
admin.site.register(ProfileUser,ProfileUserAdmin)
admin.site.register(Revenus)
admin.site.register(Depenses)
admin.site.register(Dettes)
admin.site.register(Secutity)
admin.site.register(DocumentSigne)
