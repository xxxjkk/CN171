import datetime
import os
from io import BytesIO

from django.db import transaction
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.http import urlquote
from openpyxl import Workbook, load_workbook
import json

from CN171_tools.common_api import to_ints

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

from CN171_background.api import pages, get_object
from CN171_audit.models import staffInfo


def infoManagement(request):
    staff_List = staffInfo.objects.all()
    staff_info_list = []
    for staff in staff_List:
        staff_id = staff.staff_id
        staff_name = staff.staff_name
        staff_4AAccount = staff.staff_4AAccount
        staff_account = staff.staff_account
        staff_group = staff.staff_group
        staff_system = staff.staff_system
        staff_post = staff.staff_post
        staff_status = staff.staff_status
        staff_info = {"staff_id": staff_id, "staff_name": staff_name,
                      "staff_4AAccount": staff_4AAccount, "staff_account": staff_account,
                      "staff_group": staff_group, "staff_system": staff_system,
                      "staff_post": staff_post, "staff_status": staff_status}
        staff_info_list.append(staff_info)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(staff_info_list,
                                                                                                request)
    return render(request, "audit/information.html", locals())


def staffAdd(request):
    if request.method == "POST":
        staff_name = request.POST['staff_name']
        staff_4AAccount = request.POST['staff_4AAccount']
        staff_account = request.POST['staff_account']
        staff_group = request.POST['staff_group']
        staff_system = request.POST['staff_system']
        staff_post = request.POST['staff_post']
        staff_status = request.POST['staff_status']
        staff = staffInfo()
        staff.staff_name = staff_name
        staff.staff_4AAccount = staff_4AAccount
        staff.staff_account = staff_account
        staff.staff_group = staff_group
        staff.staff_system = staff_system
        staff.staff_post = staff_post
        staff.staff_status = staff_status
        staff.save()
        status = 1
        return render(request, "audit/informationAdd.html", locals())
    else:
        display_control = "none"
        return render(request, "audit/informationAdd.html", locals())


def staffMod(request, staff_id):
    staff = get_object(staffInfo, staff_id=staff_id)
    if request.method == "POST":
        staff_name = request.POST['staff_name']
        staff_4AAccount = request.POST['staff_4AAccount']
        staff_account = request.POST['staff_account']
        staff_group = request.POST['staff_group']
        staff_system = request.POST['staff_system']
        staff_post = request.POST['staff_post']
        staff_status = request.POST['staff_status']
        staff.staff_name = staff_name
        staff.staff_4AAccount = staff_4AAccount
        staff.staff_account = staff_account
        staff.staff_group = staff_group
        staff.staff_system = staff_system
        staff.staff_post = staff_post
        staff.staff_status = staff_status
        staff.save()
        status = 1
        return render(request, "audit/informationMod.html", locals())
    else:
        display_control = "none"
        return render(request, "audit/informationMod.html", locals())


def staffDel(request):
    staff_ids = request.POST.getlist('ids', [])
    ret = "True"
    for staff_id in staff_ids:
        try:
            staffInfo.objects.filter(staff_id=staff_id).delete()
        except:
            ret = "False"
    return JsonResponse({'ret': ret})


def importStaffInfo(request):
    ret = {'msg': "上传成功！"}
    file_obj = request.FILES.get('staffInfoFile')
    if file_obj:
        type_excel = file_obj.name.split('.')[1]
        if type_excel in ['xlsx', 'xls']:
            # 开始解析上传的excel表格
            wb = load_workbook(file_obj)
            table = wb.get_sheet_by_name(wb.get_sheet_names()[0])
            nrows = table.max_row
            with transaction.atomic():
                for i in range(2, nrows + 1):
                    name = table.cell(row=i, column=1).value
                    try:
                        staff = staffInfo.objects.get(staff_name=name)
                        staff.staff_name = table.cell(row=i, column=1).value
                        staff.staff_4AAccount = table.cell(row=i, column=2).value
                        staff.staff_account = table.cell(row=i, column=3).value
                        staff.staff_group = table.cell(row=i, column=4).value
                        staff.staff_system = table.cell(row=i, column=5).value
                        staff.staff_post = table.cell(row=i, column=6).value
                        staff.staff_status = table.cell(row=i, column=7).value
                        staff.save()
                    except Exception as e:
                        if str(e) == "staffInfo matching query does not exist.":
                            staff = staffInfo()
                            staff.staff_name = table.cell(row=i, column=1).value
                            staff.staff_4AAccount = table.cell(row=i, column=2).value
                            staff.staff_account = table.cell(row=i, column=3).value
                            staff.staff_group = table.cell(row=i, column=4).value
                            staff.staff_system = table.cell(row=i, column=5).value
                            staff.staff_post = table.cell(row=i, column=6).value
                            staff.staff_status = table.cell(row=i, column=7).value
                            staff.save()
                        else:
                            ret['msg'] = "出现错误：%s" % e
                            break
        else:
            ret['msg'] = "上传文件格式不是xlsx或xls！"
    else:
        ret['msg'] = "请选择上传的文件！"
    v = json.dumps(ret)
    return HttpResponse(v)


def exportStaffInfo(request):
    staff_ids = to_ints(request.GET.get('ids'))
    wb = Workbook()
    wb.encoding = "utf-8"
    sheet1 = wb.active
    sheet1.title = "部门人员信息"
    row_one = ['姓名', '4A主账号', '从账号', '所在组', '系统', '职责', '状态']
    for i in range(1, len(row_one) + 1):
        sheet1.cell(row=1, column=i).value = row_one[i - 1]
    if staff_ids == [-1]:
        staffs = staffInfo.objects.all()
        for staff in staffs:
            cur_row = sheet1.max_row + 1
            staff_info = [staff.staff_name, staff.staff_4AAccount, staff.staff_account, staff.staff_group,
                          staff.staff_system, staff.staff_post, staff.staff_status]
            for i in range(1, len(staff_info) + 1):
                sheet1.cell(row=cur_row, column=i).value = staff_info[i - 1]
    else:
        for staff_id in staff_ids:
            staff = get_object(staffInfo, staff_id=staff_id)
            cur_row = sheet1.max_row + 1
            staff_info = [staff.staff_name, staff.staff_4AAccount, staff.staff_account, staff.staff_group,
                          staff.staff_system, staff.staff_post, staff.staff_status]
            for i in range(1, len(staff_info) + 1):
                sheet1.cell(row=cur_row, column=i).value = staff_info[i - 1]
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response = HttpResponse(output.getvalue(), content_type='application/vnd.ms-excel')
    time = datetime.datetime.now().strftime('%Y-%m-%d')
    file_name = '部门人员信息%s.xlsx' % time
    file_name = urlquote(file_name)
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name
    return response


def staffSearch(request):
    staff_name = request.GET.get('staff_name_search')
    print(staff_name)
    if staff_name == "":
        staff = staffInfo.objects.all()
    else:
        staff = staffInfo.objects.filter(staff_name=staff_name)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(staff, request)
    return render(request, "audit/information.html", locals())


def accountAudit(request):
    return render(request, "audit/accountAudit.html", locals())
