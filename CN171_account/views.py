from django.shortcuts import render

from CN171_account.forms import accFrom
from CN171_login import models
from CN171_background.api import pages, get_object
from django.http import HttpResponse, JsonResponse, FileResponse

# Create your views here.

#用户管理主页面
def userManagement(request):
    user_List = models.User.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(user_List, request)
    return render(request, "account/user_management.html", locals())

#添加用户
def userAdd(request):
    status = 0
    if request.method == "POST":
        accfrom = accFrom(request.POST)
        if accfrom.is_valid():
            accfrom.save()
            status = 1
            tips = u"新增成功！"
            display_control = ""
        else:
            status = 2
            tips = u"新增失败！"
            display_control = ""
        return render(request, "account/user_add.html", locals())
    else:
        display_control = "none"
        accfrom = accFrom()
        return render(request, "account/user_add.html", locals())


#添加用户
def userDel(request):
    acc_user_ids = request.POST.getlist('ids', [])
    returnmsg = "True"
    for acc_user_id in acc_user_ids:
        try:
            models.User.objects.filter(acc_user_id=acc_user_id).delete()
        except:
            returnmsg = "False"
    return JsonResponse({'ret': returnmsg})

#编辑用户
def userEdit(request,acc_user_id):
    status = 0
    obj = get_object(models.User, acc_user_id = acc_user_id)

    if request.method == 'POST':
        accfrom = accFrom(request.POST, instance=obj)
        if accfrom.is_valid():
            accfrom.save()
            status = 1
        else:
            status = 2
    else:
        bgform = accFrom(instance=obj)
    return render(request, 'account/user_edit.html', locals())