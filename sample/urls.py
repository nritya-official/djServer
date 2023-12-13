# myapp/urls.py
from django.urls import path
from .views import getsquare, getcube, gettesseracted, getsursolid, get_all_data

urlpatterns = [
    path('getsquare/', getsquare, name='getsquare'),
    path('getcube/', getcube, name='getcube'),
    path('gettesseracted/', gettesseracted, name='gettesseracted'),
    path('getsursolid/', getsursolid, name='getsursolid'),
    path('get_all_data/', get_all_data, name='get_all_data'),
]
