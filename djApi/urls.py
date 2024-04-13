# djServer/djApi/urls.py
from django.urls import path
from .views import landing_page, get_all_data, search, autocomplete, help, landingPageImages, studioFullPage,ratingChange,getRating

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('get_all_data/', get_all_data, name='get_all_data'),
    path('search/', search, name='search'),
    path('autocomplete/', autocomplete, name='autocomplete'),
    path('help/', help, name='help'),
    path('landingPageImages/', landingPageImages, name='landingPageImages'),
    path('studioFullPage/<str:studioId>', studioFullPage, name='studioFullPage'),
    path('ratingChange/', ratingChange, name='ratingChange'),
    path('getRating/<str:studioId>/<str:userId>/', getRating, name='getRating'),
]
