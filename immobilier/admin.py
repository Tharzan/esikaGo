from django.contrib import admin

from immobilier.models import *

class SavePropertyAdmin(admin.ModelAdmin):
    list_display = ('user','type_bien', 'adresse','statut',
                   'montant', 'id_maison','nom_complet_occupant','tel_occupant', 'date_entrer',
                     'garantie','contratBail')
class LoyerAdmin(admin.ModelAdmin):
    list_display =('id','property','montant','mois','date_payement','observation','date_creation',
    'annee','url_document','qr_document')
admin.site.register(PostMaison)
admin.site.register(SaveProperty,SavePropertyAdmin)
admin.site.register(ImageMaisons)
admin.site.register(Loyer,LoyerAdmin)
admin.site.register(Document)
