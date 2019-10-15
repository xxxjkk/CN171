import datetime

from django.db.models import Q
from django.http import HttpResponse
from CN171_cmdb import models,forms
from django.shortcuts import render, redirect
from CN171_cmdb.models import CmdbHost,CmdbApp,HostPwdOprLog
from CN171_cmdb.forms import DetailLogForm, HostPwdEditForm,NormalUserForm
from CN171_background.api import pages
from CN171_tools.common_api import export_download_txt
from CN171_tools.connecttool import *
from CN171_tools.sftputils import *
import json

# Create your views here.

#def cmdbIndex(request):
#    return render(request, "cmdb/index.html", locals())
def text_save(filename, data):  # filename为写入CSV文件的路径，data为要写入数据列表.
    file = open(filename, 'a')
    for i in range(len(data)):
        s = str(data[i]).replace('[', '').replace(']', '')  # 去除[],这两行按数据不同，可以选择
        s = s.replace("'", '').replace(',', '') + '\n'  # 去除单引号，逗号，每行末尾追加换行符
        file.write(s)
    file.close()

def hostManagement(request):
    host_list = []
    keyword = request.GET.get("keyword", "")
    if keyword:
        host_list = models.CmdbHost.objects.filter(
            Q(cmdb_host_name__icontains=keyword) |
            Q(cmdb_host_type__icontains=keyword) |
            Q(cmdb_host_pod__icontains=keyword) |
            Q(cmdb_host_busip__icontains=keyword) |
            Q(cmdb_host_manip__icontains=keyword) |
            Q(cmdb_host_status__icontains=keyword)
        )
    else:
        host_list = models.CmdbHost.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(host_list, request)
    return render(request, "cmdb/host_management.html", locals())

def appManagement(request):
    app_list = []
    keyword = request.GET.get("keyword", "")
    if keyword:
        app_list = models.CmdbApp.objects.filter(
            Q(app_name__icontains=keyword) |
            Q(app_status__icontains=keyword)
        )
    else:
        app_list = models.CmdbApp.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(app_list, request)
    return render(request, "cmdb/app_management.html", locals())

#跳转到主机用户密码日志页面
def hostPwdOprLogPage(request):
    host_pwd_opr_log_list = models.HostPwdOprLog.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(host_pwd_opr_log_list, request)
    return render(request, "cmdb/host_pwd_opr_log.html", locals())

#主机用户密码操作日志列表
def hostPwdOprLog(request):
    host_pwd_opr_log_list = []
    keyword = request.GET.get("keyword", "")
    starttime = request.GET.get('starttime')
    endtime = request.GET.get('endtime')
    host_pwd_opr_log_list = models.HostPwdOprLog.objects.all()
    if keyword:
        host_pwd_opr_log_list = host_pwd_opr_log_list.filter(
            Q(opr_user_name__icontains=keyword)
        )
    if starttime:
        host_pwd_opr_log_list=host_pwd_opr_log_list.filter(opr_time__gte =starttime)
    if endtime:
        host_pwd_opr_log_list= host_pwd_opr_log_list.filter(opr_time__lte =endtime)

    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(host_pwd_opr_log_list, request)
    return render(request, "cmdb/host_pwd_opr_log.html", locals())

#主机用户密码详细日志
def hostPwdDetailLog(request):
        logId = request.GET.get("logId")
        flag = request.GET.get("flag")
        obj1 = HostPwdOprLog.objects.get(id= logId)
        if flag == '1':
            return  export_download_txt(obj1.detail_log)
        detailLogForm = DetailLogForm(instance=obj1)
        return render(request, "cmdb/host_pwd_detail_log.html", locals())


#跳转到主机用户密码修改页面
def redEditHostPwdPage(request):
    form = HostPwdEditForm()
    return render(request, "cmdb/host_pwd_edit.html", locals())

#修改主机用户密码
def editHostPwd(request):
    form = HostPwdEditForm(request.POST, request.FILES)
    ret = {'status': True, 'msg': None}
    if form.is_valid():
        file_obj = request.FILES.get('modified_host_list_file')
        modified_host_user =request.POST.get("modified_host_user")
        old_password = request.POST.get("old_password")
        new_password1 = request.POST.get("new_password1")
        username = request.session['user_name']

        file_path = os.path.join(BASE_DIR, "temp")
        path_not_exist_create(file_path)
        file_name_path=os.path.join(file_path,file_obj.name)
        try:
            #将文件从客户机浏览器写入到服务器
            f = open(file_name_path, 'wb')
            # chunks表示一块块的
            for line in file_obj.chunks():
                f.write(line)
            f.close()
            #将服务器文件sftp到Ansible主机
            client, sftp=sftpconnect("CMIOT")
            remote_path="/home/baiyang"
            flag=put(sftp,file_name_path, remote_path)
            sftpDisconnect(client)
            #执行命令
            if(flag):
                cmd="ansible -i %s all -u ansbmk -k -b -K -f 500 -m shell -a 'echo %s:%s|chpasswd'" \
                    %(remote_path,modified_host_user,old_password)
                cmd1="%s" %("bY!123456")
                cmd2 = "%s" % ("bY!123456")
                ssh_fd = ssh_connect("Ansible")
                stdin, stdout, stderr=ssh_exec_cmd(ssh_fd, cmd)
                stdin1, stdout1, stderr1=ssh_exec_cmd(ssh_fd, cmd1)
                stdin2, stdout2, stderr2=ssh_exec_cmd(ssh_fd, cmd2)
                ssh_close(ssh_fd)
                #保存操作记录
                hostPwdOprLog=HostPwdOprLog()
                hostPwdOprLog.opr_log_save(username,modified_host_user,"失败",datetime.datetime.now(),stdout2)
                ret['status'] = True
                ret['msg'] = "修改成功！"
        except Exception as e:
            print(e)
    else:
        ret['status'] = False
        ret['msg'] = form.errors  # 这是一个对象
        print(form.errors)
    v = json.dumps(ret)  # 转换为字典类型
    return HttpResponse(v)

