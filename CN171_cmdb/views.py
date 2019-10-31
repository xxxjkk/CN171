import datetime
import time

from django.db.models import Q
from django.http import HttpResponse
from CN171_cmdb import models,forms
from django.shortcuts import render, redirect
from CN171_cmdb.models import CmdbHost, CmdbApp, HostPwdOprLog, CmdbAppCluster
from CN171_cmdb.forms import DetailLogForm, HostPwdEditForm, NormalUserForm, CmdbHostForm
from CN171_background.api import pages, get_object
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
        app_list = models.CmdbAppCluster.objects.filter(
            Q(app_name__icontains=keyword) |
            Q(app_status__icontains=keyword)
        )
    else:
        cluster_list = models.CmdbAppCluster.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(cluster_list, request)
    return render(request, "cmdb/app_management.html", locals())

#批量删除应用
def appDel(request):
    if request.method == 'POST':
        app_batch = request.GET.get('arg', '')
        app_id_all = str(request.POST.get('app_id_all', ''))

        if app_batch:
            for app_id in app_id_all.split(','):
                bg_item = get_object(CmdbHost, cmdb_host_id=app_id)
                bg_item.delete()
    return HttpResponse(u'删除成功')

#集群下的APP详情
def clusterAppDetail(request):
    clusterId=request.GET.get("clusterId")
    cluster_app_detail_list = models.CmdbApp.objects.filter( cluster_id=clusterId)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(cluster_app_detail_list,
                                                                                                request)
    return render(request, "cmdb/cluster_app_detail.html", locals())

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
    ret = {'status': False, 'msg': None,'form_status': True, 'msg1':None}
    opr_result = "失败"
    if form.is_valid():
        detail_log_info = ""
        file_obj = request.FILES.get('modified_host_list_file')
        modified_host_user =request.POST.get("modified_host_user")
        old_password = request.POST.get("old_password")
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
            remote_path=get_init_parameter2('Ansible')
            flag=put(sftp,file_name_path, remote_path)
            sftpDisconnect(client)
            #执行命令
            if(flag):
                detail_log_info, retStr = excute_edit_commond(remote_path, modified_host_user, old_password)
                if retStr:
                    ret['status'] = True
                    ret['msg'] = "修改成功！"
                    opr_result="成功"
                else:
                    ret['msg'] = "修改失败，详细信息请查看日志！"
            else:
                ret['msg'] = "上传文件失败！"
        except Exception as e:
            print(e)
        # 保存操作记录
        hostPwdOprLog = HostPwdOprLog()
        hostPwdOprLog.opr_log_save(username, modified_host_user, opr_result, datetime.datetime.now(), detail_log_info)
    else:
        ret['msg1'] = form.errors  # 这是一个对象
        print(form.errors)
    v = json.dumps(ret)  # 转换为字典类型
    return HttpResponse(v)


#登录到相应的主机执行修改命令
def excute_edit_commond(remote_path, modified_host_user, old_password):
    retStr = False
    #修改主机密码的命令
    cmd = "ansible -i %s all -u ansbmk -k -b -K -f 500 -m shell -a 'echo %s:%s|chpasswd'\r" \
          % (remote_path, modified_host_user, old_password)
    #ansible普通用户密码
    ansible_general_host_pwd,ansible_root_host_pwd = get_init_parameter1("Ansible")
    cmd1 = "%s" % (ansible_general_host_pwd+"\r")
    #ansibile root用户密码
    cmd2 = "%s" % (ansible_root_host_pwd+"\r")
    trans, channel = build_shell_channel("Ansible")
    # 发送要执行的命令
    channel.send(cmd)
    while True:
        time.sleep(0.2)
        rst = channel.recv(1024)
        rst = rst.decode('utf-8')
        print(rst)
        # 通过命令执行提示符来判断命令是否执行完成
        if 'SSH password' in rst:
            channel.send(cmd1)  # SSH password  普通用户密码
            time.sleep(0.5)
            ret = channel.recv(1024)
            ret = ret.decode('utf-8')
            print(ret)
            if "SUDO password" in ret:
                channel.send(cmd2)  # ansibile主机 root用户密码
                time.sleep(0.5)
                detail_log = channel.recv(1024)
                detail_log = detail_log.decode('utf-8')
                print(detail_log)
                if "FAILED" not in detail_log and "SUCCESS" in detail_log:
                    retStr = True
                break
    close_shell_channel(trans, channel)
    return detail_log, retStr

#GET是跳转到用户主机页面，POST是添加主机
def hostAddPage(request):
    if request.method == "GET":
        form = CmdbHostForm()
        return render(request, 'cmdb/host_add.html', locals())
    else:
        ret = {'status': False, 'msg': '添加主机失败！','msg1':None}
        hostForm = CmdbHostForm(request.POST)
        if hostForm.is_valid():
            hostForm.save()
            ret['status'] = True
            ret['msg'] = "添加主机成功！"
        else:
            ret['msg1'] = hostForm.errors  # 这是一个对象
            print(hostForm.errors)
        v = json.dumps(ret)  # 转换为字典类型
        return HttpResponse(v)


#批量删除主机
def hostDel(request):
    if request.method == 'POST':
        host_batch = request.GET.get('arg', '')
        host_id_all = str(request.POST.get('host_id_all', ''))

        if host_batch:
            for cmdb_host_id in host_id_all.split(','):
                bg_item = get_object(CmdbHost, cmdb_host_id=cmdb_host_id)
                bg_item.delete()
    return HttpResponse(u'删除成功')

