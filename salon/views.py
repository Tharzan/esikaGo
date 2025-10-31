from django.shortcuts import render

def listeSalon(request):
    liste = [1,3,3,3,3,3]
    return render(request, 'salon/liste_salon.html', locals())
