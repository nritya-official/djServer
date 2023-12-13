from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def getsquare(request):
    query = int(request.GET.get('query', 0))
    result = query ** 2
    return JsonResponse({'result': result})

def getcube(request):
    query = int(request.GET.get('query', 0))
    result = query ** 3
    return JsonResponse({'result': result})

def gettesseracted(request):
    query = int(request.GET.get('query', 0))
    result = query ** 4
    return JsonResponse({'result': result})

def getsursolid(request):
    query = int(request.GET.get('query', 0))
    result = query ** 5
    return JsonResponse({'result': result})

def get_all_data(request):
    # Assuming you have some data to return in an array
    data = []
    query = int(request.GET.get('query', 0))
    data = [query**2, query**3, query**4, query**5]
    return JsonResponse({'data': data})
