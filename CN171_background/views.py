from django.http import HttpResponse
from django.shortcuts import render
from CN171_background import models
from CN171_background.api import pages
from django.shortcuts import render,redirect
from CN171_background.models import BgTaskManagement
from CN171_tools import connecttool
from django.db.models import Q

# Create your views here.

#后台管理函数
def taskManagement(request):
    # 获取所有后台对象
    # page_len = request.GET.get('page_len', '')
    task_list=[]
    keyword = request.GET.get("keyword","")
    if keyword:
        task_list=models.BgTaskManagement.objects.filter(
            Q(bg_module__icontains = keyword ) |
            Q(bg_domain__icontains = keyword ) |
            Q(bg_status__icontains = keyword)  |
            Q(bg_lastopr_user__icontains = keyword) |
            Q(bg_lastopr_type__icontains =keyword)  |
            Q(bg_lastopr_result__icontains= keyword)
        )
    else:
        task_list = models.BgTaskManagement.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(task_list, request)
    return render(request, "background/task_management.html", locals())


#单个按钮执行函数
def taskExecuteOne(request):
    bg_id = request.GET.get('bg_id')
    bg_action = request.GET.get('bg_action')
    bgTaskManagement = BgTaskManagement.objects.get(bg_id=bg_id)

    if bg_action == 'start':
        cmd = bgTaskManagement.bg_task_start
    elif bg_action == 'stop':
        cmd = bgTaskManagement.bg_task_stop
    elif bg_action == 'restart':
        cmd = bgTaskManagement.bg_task_restart
    else:
        return redirect("taskManagement")

    connecttool.domainExecuteOne(cmd)
    return redirect("taskManagement")

