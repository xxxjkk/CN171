from django.shortcuts import render

# Create your views here.

def configManagement(request):

    return render(request,"config/config_management.html",locals())