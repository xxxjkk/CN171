from django.shortcuts import render
from CN171_background import models

# Create your views here.

#后台管理
def taskManagement(request):
    task_list = models.BgTaskManagement.objects.all()
    return render(request, "background/task_management.html", {"task_list" : task_list})

