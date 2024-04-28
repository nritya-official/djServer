import os

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from django.http import JsonResponse

import jwt


def sign_in(request):
    setup = settings.SETUP
    if setup == "LOCAL":
        login_uri = "http://localhost:8000/socialAuthApp/auth-receiver"
    elif setup == "HEROKU":
        login_uri = "https://nrityaserver-2b241e0a97e5.herokuapp.com/socialAuthApp/auth-receiver"
    return render(request, 'sign_in.html', {'login_uri': login_uri})


@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    token = request.POST['credential']
    
    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), "847422777654-s07i1orl5v5igsoh8vthigptf5ist627.apps.googleusercontent.com"
        )
        print(user_data.get("email"))
    except ValueError:
        return HttpResponse(status=403)

    # In a real app, I'd also save any new user here to the database. See below for a real example I wrote for Photon Designer.
    # You could also authenticate the user here using the details from Google (https://docs.djangoproject.com/en/4.2/topics/auth/default/#how-to-log-a-user-in)
    request.session['user_data'] = user_data

    #return redirect('sign_in')
    return render(request, 'close_browser.html', {'user_data_json': (user_data)})



def sign_out(request):
    del request.session['user_data']
    return redirect('sign_in')
