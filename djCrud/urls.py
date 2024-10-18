from django.urls import path
from .views import *
urlpatterns = [
    path('testEndpoint/', crudTest, name='crudTest'),
    path('newEntity/', newEntity, name='newEntity'),
    # Add more paths as needed availFreeTrialResults
]
