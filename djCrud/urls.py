from django.urls import path
from .views import *
urlpatterns = [
    path('', testEndpoint, name='testEndpoint'),
    path('newEntity/', newEntity, name='newEntity'),
    path('updateEntity/<str:entity_id>', updateEntity, name='updateEntity'),
    path('kycApproval/<str:kyc_id>', kycApproval, name='kycApproval'),
    path('getKyc/', getKyc, name='getKyc'),
    path('getKycDoc/<str:kyc_id>', getKycDoc, name='getKycDoc'),
    # Add more paths as needed availFreeTrialResults
]
