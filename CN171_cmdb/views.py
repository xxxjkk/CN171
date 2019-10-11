from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from CN171_cmdb import models,forms
from CN171_background.api import pages
from django.shortcuts import render, redirect
from CN171_cmdb.models import CmdbHost,CmdbApp,HostPwdOprLog
from CN171_cmdb.forms import DetailLogForm, HostPwdEditForm
from CN171_background.api import pages
from CN171_tools.common_api import export_download_txt

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

def hostPwdOprLog(request):
    host_pwd_opr_log_list = []
    keyword = request.GET.get("keyword", "")
    starttime = request.GET.get('starttime')
    endtime = request.GET.get('endtime')

    if keyword:
        host_pwd_opr_log_list = models.HostPwdOprLog.objects.filter(
            Q(opr_user_name__icontains=keyword)
        )
    else:
        host_pwd_opr_log_list = models.HostPwdOprLog.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(host_pwd_opr_log_list, request)
    return render(request, "cmdb/host_pwd_opr_log.html", locals())

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
    form= HostPwdEditForm(request.POST)
    if form.is_valid():
        print('Do somethings!')
        tips = u"新增成功！"
        return render(request, "cmdb/host_pwd_edit.html", locals())
    else:
        tips = u"新增失败！"
        form = HostPwdEditForm(request.POST)
        return render(request, "cmdb/host_pwd_edit.html", locals())

