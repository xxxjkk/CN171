from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse,HttpResponse
from CN171_crontab import tasks

def addaction(request):
    res = tasks.bgaction.delay()
    #任务逻辑
    return JsonResponse({'status':'successful','task_id':res.task_id})
