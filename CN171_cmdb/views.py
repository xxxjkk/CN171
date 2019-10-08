from django.shortcuts import render

# Create your views here.

def hostManagement(request):
    return render(request, "cmdb/index.html", locals())


def appManagement(request):
    return render(request, "cmdb/app_management.html", locals())