from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from CN171_cmdb import models
from CN171_background.api import pages
from django.shortcuts import render, redirect
from CN171_cmdb.models import CmdbHost,CmdbApp

# Create your views here.

#def cmdbIndex(request):
#    return render(request, "cmdb/index.html", locals())

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
    if keyword:
        host_pwd_opr_log_list = models.HostPwdOprLog.objects.filter(
            Q(opr_user_name__icontains=keyword)
        )
    else:
        host_pwd_opr_log_list = models.HostPwdOprLog.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(host_pwd_opr_log_list, request)
    return render(request, "cmdb/host_pwd_opr_log.html", locals())