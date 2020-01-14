import os, zipfile
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, Count
from django.template.loader import render_to_string

from CN171_operation.models import *
from CN171_operation.forms import *
from CN171_operation.action import *
from CN171_background.api import pages
from CN171_operation.tasks import *
from CN171_tools.sftputils import *

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

#读取配置文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/operation.conf'),encoding='utf-8')

#CMIOT账务文件管理主方法
def cFinanceMgnt(request):
    finance_list = OprFinance.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
        finance_list, request)
    area_list = config.get('Finance', 'finance_area').split(', ')
    checkresult_list = config.get('Finance', 'finance_checkresult').split(', ')
    return render(request, "operation/cmiotFinanceManagement.html", locals())

#CMIOT账务文件管理页面查询方法
def cFinanceMgntSearch(request):
    monthpicker = request.POST.get('monthpicker')
    arealist = request.POST.getlist('area_list')
    resultlist = request.POST.getlist('result_list')

    #将3个查询条件进行或查询
    finance_list = OprFinance.objects.filter(Q(opr_cycle=monthpicker)|Q(opr_area__in=arealist)
                                             |Q(opr_check_result__in=resultlist))

    #获取模板内容
    content_html = render_to_string('operation/finance_list.html', {'finance_list': finance_list})
    #组装返回结果
    result = {'flag': "success", 'msg': '', 'html': content_html}

    return JsonResponse(result)

#CMIOT账务文件管理页面——上传页面跳转方法
def cFinanceMgntUploadGoto(request):
    uploadform = cFinanceMgntUploadForm()
    return render(request, "operation/cmiotfinancefileupload.html", locals())

#CMIOT账务文件管理页面——上传处理方法
def cFinanceMgntUpload(request):
    #获取form对象
    uploadform = cFinanceMgntUploadForm(request.POST, request.FILES)
    result = {'flag': '', 'msg': ''}

    #判断校验结果
    if uploadform.is_valid():
        #全部校验通过，获取文件对象
        file_obj = request.FILES.get('finance_file')
        #配置上传目录
        file_path_local = config.get('Finance', 'finance_localfiledirtmp')
        file_name_path_local = os.path.join(file_path_local, file_obj.name)
        path_not_exist_create(file_path_local)

        # 判断文件类型
        file_ext = file_obj.name.split('.')[-1]
        # if ('zip' == file_ext) or ('gz' == file_ext):
        if file_ext in ['zip', 'gz']:
            #文件上传
            try:
                #判断文件是否存在
                if(os.path.isfile(file_name_path_local)):
                    #组装返回结果
                    result['flag'] = "false"
                    result['msg'] = "文件名已存在，请上传新文件！"
                else:
                    #将文件从客户机浏览器写入到CN171服务器
                    f = open(file_name_path_local, 'wb')
                    #以chunks形式写入
                    for line in file_obj.chunks():
                        f.write(line)
                    f.close()

                    #解压zip文件
                    if 'zip' == file_ext:
                        zip_file = zipfile.ZipFile(file_name_path_local)
                        zip_list = zip_file.namelist()
                        for f in zip_list:
                            #循环解压文件到指定目录
                            filename = f
                            print('filename :', filename)
                            zip_file.extract(filename, file_path_local)
                        zip_file.close()

                    #调用分拣方法进行文件分拣
                    cFinanceMgntClassifyTask.delay()

                    #调用校验方法进行文件校验

                    #将服务器文件sftp到账务文件稽核服务器
                    #cFinanceFileUploadTask.delay()

                    #组装返回结果
                    result['flag'] = "success"
                    result['msg'] = "文件上传成功，正在进行后台分拣校验，稍后请刷新页面！"
            except Exception as e:
                print(e)
        else:
            # 组装返回结果
            result['flag'] = "false"
            result['msg'] = "文件名校验异常，请确认后重新上传！"
    else:
        # 组装返回结果
        result['flag'] = "false"
        result['msg'] = "校验异常，请重新上传！"

    return render(request, "operation/cmiotfinancefileupload.html", locals())


#CMIOT账务文件管理页面——下载页面跳转方法
def cFinanceMgntDownloadGoto(request):
    area_list = config.get('Finance', 'finance_area').split(', ')
    type_list = config.get('Finance', 'finance_filetype_CN').split(', ')
    cycle_list = OprFinance.objects.values('opr_cycle').annotate(count=Count('opr_cycle')).order_by('-opr_cycle')
    return render(request, "operation/cmiotfinancefiledownload.html", locals())

#CMIOT账务文件管理页面——下载处理方法
def cFinanceMgntDownload(request):
    return

#CMIOT账务文件管理页面——文件详情页面跳转方法
def cFinanceFileDetail(request):
    type = request.GET.get('type')
    id = request.GET.get('id')
    file_list = OprFinanceFiledetail.objects.filter(Q(opr_finance=id)&Q(opr_finance_filedetail_type=type))
    return render(request, "operation/cmiotfinancefiledetail.html", locals())


#CMIOT账务文件管理页面——文件校验页面跳转
def cFinanceFileCheckDetail(request):
    id = request.GET.get('id')
    checkresult = OprFinanceCheckDetail.objects.get(opr_finance=id)
    return render(request, "operation/cmiotfinancefilecheck.html", locals())

#CMIOT账务文件稽核主方法
def cFinanceReco(request):

    return render(request, "operation/cmiotFinanceReco.html", locals())







