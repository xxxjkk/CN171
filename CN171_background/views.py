import sys

from django.http import HttpResponse
from django.shortcuts import render
from CN171_background import models
from CN171_background.models import BgTaskManagement
from CN171_background.tool import app_stop, ssh_exec_cmd, ssh_close
from CN171_background.tool import ssh_connect
from django.shortcuts import redirect


# Create your views here.

#后台管理函数
def taskManagement(request):
    #获取所有后台对象
    task_list = models.BgTaskManagement.objects.all()
    return render(request, "background/task_management.html", {"task_list" : task_list})


#单个启动按钮函数
def taskStart(request):
    bg_id = request.GET.get('bg_id')
    bgTaskManagement = BgTaskManagement.objects.get(bg_id=bg_id)

    sshd = ssh_connect()
    cmd = bgTaskManagement.bg_task_start
    stdin, stdout, stderr = ssh_exec_cmd(sshd, cmd)
    err_list = stderr.readlines()
    if len(err_list) > 0:
        print('Start failed:' + err_list[0])
        sys.exit(0)
    else:
        print('Start success.')
    for item in stdout.readlines():
        print(item)
    ssh_close(sshd)

    return redirect("taskManagement")