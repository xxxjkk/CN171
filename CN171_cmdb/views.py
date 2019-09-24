from django.shortcuts import render

# Create your views here.

def cmdbIndex(request):
    return render(request, "cmdb/index.html", locals())