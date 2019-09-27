from django.shortcuts import render,redirect
from CN171_background.models import BgTaskManagement
from CN171_tools import connecttool


# Create your views here.

#后台管理函数
def taskManagement(request):
    #获取所有后台对象
    task_list = BgTaskManagement.objects.all()
    return render(request, "background/task_management.html", {"task_list" : task_list})


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



#新增中心函数

