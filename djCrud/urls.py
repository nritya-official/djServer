from django.urls import path
from .views import *
urlpatterns = [
    path('', testEndpoint, name='testEndpoint'),
    path('newEntity/', newEntity, name='newEntity'),
    path('updateEntity/<str:entity_id>', updateEntity, name='updateEntity'),
    # Add more paths as needed availFreeTrialResults
]
