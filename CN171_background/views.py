
import sys
import threading

from django.http import HttpResponse
from django.shortcuts import render
from CN171_background import models
from CN171_background.api import pages,get_object
from django.shortcuts import render, redirect
from CN171_background.models import BgTaskManagement, BgTaskLog
from CN171_tools import connecttool
from CN171_background.forms import BgForm
from datetime import datetime

# Create your views here.

# 后台管理函数
from CN171_tools.connecttool import ssh_close, ssh_connect, ssh_exec_cmd


def taskManagement(request):
    # 获取所有后台对象
    # page_len = request.GET.get('page_len', '')
    task_list = models.BgTaskManagement.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
        task_list, request)
    return render(request, "background/task_management.html", locals())


# 单个按钮执行函数
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


def batchTaskStart(request):
    bg_ids = request.POST.getlist('ids', [])
    sshd = ssh_connect()
    threads = []
    for bg_id in bg_ids:
        bgTaskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
        cmd = bgTaskManagement.bg_task_start
        print(bgTaskManagement.bg_task_start)
        task = MyThread(ssh_exec_cmd, args=(sshd, cmd))
        threads.append(task)
      # start threads 此处并不会执行线程，而是将任务分发到每个线程，同步线程。等同步完成后再开始执行start方法
        task.start()
        print(task.getName())
    for i in threads:
        i.join()
        stdin, stdout, stderr = i.get_result()
        err_list = stderr.readlines()
        if len(err_list) > 0:
            print('Start failed:' + err_list[0])
            for bg_id in bg_ids:
                taskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
                taskManagement.bg_lastopr_user = request.session['user_name']
                taskManagement.bg_lastopr_time = datetime.now()
                taskManagement.bg_lastopr_result = "失败"
                taskManagement.bg_lastopr_type = "启动"
                bg_log = BgTaskLog()
                bg_log.bg_id = bg_id
                bg_log.bg_operation = "启动" + taskManagement.bg_module + taskManagement.bg_domain
                bg_log.bg_operation_time = datetime.now()
                bg_log.bg_operation_user = request.session['user_name']
                bg_log.bg_opr_result = "失败"
                taskManagement.bg_insert_time = datetime.now()
                taskManagement.save()
                # 写入日志文件
                file_name = "bg_log" + datetime.now().strftime("%Y-%m-%d")
                bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                    bg_log.bg_operation_user + bg_log.bg_operation + bg_log.bg_opr_result
                path = "D:\\运维后台\\CN171\\log" + file_name + '.txt'
                bg_log.bg_log_dir = path
                file = open(path, 'a+')
                file.write('\n' + bg_log_msg)  # msg也就是下面的Hello world!
                file.close()
                bg_log.save()
            sys.exit(0)
        else:
            print('Start success.')
            for bg_id in bg_ids:
                taskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
                taskManagement.bg_lastopr_user = request.session['user_name']
                taskManagement.bg_lastopr_result = "成功"
                taskManagement.bg_lastopr_type = "启动"
                taskManagement.bg_status = "启动"
                taskManagement.bg_lastopr_time = datetime.now()
                taskManagement.bg_insert_time = datetime.now()
                bg_log = BgTaskLog()
                bg_log.bg_id = bg_id
                bg_log.bg_operation = "启动" + taskManagement.bg_module + taskManagement.bg_domain
                bg_log.bg_operation_time = datetime.now()
                bg_log.bg_operation_user = request.session['user_name']
                bg_log.bg_opr_result = "成功"
                taskManagement.save()
                # 写入日志文件
                file_name = "bg_log" + datetime.now().strftime("%Y-%m-%d")
                # str不支持时间格式直接相加
                bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                    bg_log.bg_operation_user + bg_log.bg_operation + bg_log.bg_opr_result
                path = "D:\\运维后台\\CN171\\log\\" + file_name + ".txt"
                bg_log.bg_log_dir = path
                file = open(path, 'a+')
                file.write('\n' + bg_log_msg)  # msg也就是下面的Hello world!
                file.close()
                bg_log.save()
        for item in stdout.readlines():
            print(item + i.getName())
    ssh_close(sshd)
    return redirect("taskManagement")


# 多线程创建函数
class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            return None


def taskEdit(request, bg_id):
    status = 0
    obj = get_object(BgTaskManagement, bg_id=bg_id)

    if request.method == 'POST':
        bgform = BgForm(request.POST, instance=obj)
        if bgform.is_valid():
            bgform.save()
            status = 1
        else:
            status = 2
    else:
        bgform = BgForm(instance=obj)
    return render(request, 'background/task_edit.html', locals())

def taskAdd(request):
    status = 0
    if request.method == "POST":
        bgform = BgForm(request.POST)
        if bgform.is_valid():
            bgform.save()
            status = 1
            tips = u"新增成功！"
            display_control = ""
        else:
            status = 2
            tips = u"新增失败！"
            display_control = ""
        return render(request, "background/task_add.html", locals())
    else:
        display_control = "none"
        bgform = BgForm()
        return render(request, "background/task_add.html", locals())


def taskDel(request):
    bg_id = request.GET.get('bg_id', '')
    if bg_id:
        BgTaskManagement.objects.filter(bg_id=bg_id).delete()

    if request.method == 'POST':
        bg_batch = request.GET.get('arg', '')
        bg_id_all = str(request.POST.get('bg_id_all', ''))

        if bg_batch:
            for bg_id in bg_id_all.split(','):
                bg_item = get_object(BgTaskManagement, bg_id=bg_id)
                bg_item.delete()
    return HttpResponse(u'删除成功')