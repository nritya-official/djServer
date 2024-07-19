# djServer/djApi/urls.py
from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('get_all_data/', get_all_data, name='get_all_data'),
    path('search/', search, name='search'),
    path('autocomplete/', autocomplete, name='autocomplete'),
    path('help/', help, name='help'),
    path('landingPageImages/', landingPageImages, name='landingPageImages'),
    path('studioFullPage/<str:studioId>', studioFullPage, name='studioFullPage'),
    path('studio/<str:studioId>/text/', studioTextData,name="studioTextData"),
    path('studio/<str:studioId>/images/', studioImageURLs,name="studioImageURLs"),
    path('studioRatingChange/', studioRatingChange, name='studioRatingChange'),
    path('getStudioRating/<str:studioId>/<str:userId>/', getStudioRating, name='getStudioRating'),
     path('reviews/', views.create_review, name='create_review'),

]
