from django.shortcuts import render

def listeRestaurant(request):
    liste = [1,2,2,2,2,2,2,2,2]
    return render(request, 'restaurant/liste_restaurant.html', locals())
