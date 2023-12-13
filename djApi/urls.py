# myapp/urls.py
from django.urls import path
from .views import landing_page, get_all_data, search, autocomplete, help

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('get_all_data/', get_all_data, name='get_all_data'),
    path('search/', search, name='search'),
    path('autocomplete/', autocomplete, name='autocomplete'),
    path('help/', help, name='help'),
]
