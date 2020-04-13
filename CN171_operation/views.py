import os, zipfile
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponse
from django.db.models import Q, Count
from django.template.loader import render_to_string
from django.core.cache import cache

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
    finance_list = OprFinance.objects.all().order_by('-opr_cycle')
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
        finance_list, request)
    area_list = config.get('Finance', 'finance_area').split(', ')
    checkresult_list = config.get('Finance', 'finance_checkresult').split(', ')
    return render(request, "operation/cmiotFinanceManagement.html", locals())

#CMIOT账务文件管理页面查询方法
def cFinanceMgntSearch(request):
    #定义查询条件字典
    search_dict = dict()

    monthpicker = request.POST.get('monthpicker')
    if monthpicker:
        search_dict['opr_cycle'] = monthpicker
    area_list = request.POST.getlist('area_list')
    if area_list:
        search_dict['opr_area__in'] = area_list
    result_list = request.POST.getlist('result_list')
    if result_list:
        search_dict['opr_check_result__in'] = result_list

    #将3个查询条件进行或查询
    finance_list = OprFinance.objects.filter(**search_dict)

    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
        finance_list, request)

    #获取模板内容
    content_html = render_to_string('operation/finance_list.html',
                                    {'page_objects': page_objects, 'page_len': page_len, 'p':p,
                                     'show_first': show_first, 'show_end':show_end, 'end_page':end_page,
                                     'page_range':page_range, 'current_page':current_page})
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
    #每次下载打包文件前，将全局变量置0
    cache.set('percent', 0)

    area_list = config.get('Finance', 'finance_area').split(', ')
    type_list = config.get('Finance', 'finance_filetype_CN').split(', ')
    cycle_list = OprFinance.objects.values('opr_cycle').annotate(count=Count('opr_cycle')).order_by('-opr_cycle')
    return render(request, "operation/cmiotfinancefiledownload.html", locals())

#CMIOT账务文件管理页面——下载处理方法
def cFinanceMgntDownload(request):
    #获取文件下载目录
    doanloaddir = config.get('Finance', 'finance_downloaddir')
    if not os.path.exists(doanloaddir):
        print(u'目录%s不存在，新建目录！' % doanloaddir)
        os.makedirs(doanloaddir)

    if request.method == 'POST':
        page = request.POST.get('page')

        #根据不同的页面，采用不同的文件搜索方式
        if page == 'financedownloadmgnt':
            area_list = request.POST.getlist('area_list')
            type_list = request.POST.getlist('type_list')
            cycle_list = request.POST.getlist('cycle_list')

            financeFileZip.delay(page=page, area_list=area_list, type_list=type_list, cycle_list=cycle_list)

            back_dic = {'existflag': "存在", 'existdes': "正在后台打包，请稍后！"}
            import json
            return HttpResponse(json.dumps(back_dic))
        elif page == 'financefiledetail':
            id_list = request.POST.getlist('id_list')
            financeFileZip.delay(page=page, id_list=id_list)

            back_dic = {'existflag': "存在", 'existdes': "正在后台打包，请稍后！"}
            import json
            return HttpResponse(json.dumps(back_dic))

    elif request.method == 'GET':
        filename = request.GET.get('filename')
        if filename:
            print('filename :', filename)
            filepath = os.path.join(doanloaddir, filename)
            file = open(filepath, 'rb')

            response = FileResponse(file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{}"'.format(filename)
            return response
        else:
            #获取全局变量
            percent = cache.get('percent')
            data = {'percent':percent}
            print(u'账务文件打包完成进度 : %s' %percent + '%')
            if percent == 100:
                filename = cache.get('filename')
                data['filename']=filename
            return JsonResponse(data)

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
    financereco_list = OprFinanceReco.objects.all().order_by('-opr_finance_reco_id')
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
        financereco_list, request)
    area_list = config.get('Finance', 'finance_area').split(', ')
    recoresult_list = config.get('Finance', 'finance_recoresult').split(', ')

    return render(request, "operation/cmiotFinanceReco.html", locals())

#CMIOT账务稽核管理页面查询方法
def cFinanceRecoSearch(request):
    #定义查询条件字典
    search_dict = dict()

    monthpicker = request.POST.get('monthpicker')
    if monthpicker:
        search_dict['opr_finance__opr_cycle'] = monthpicker
    area_list = request.POST.getlist('area_list')
    if area_list:
        search_dict['opr_finance__opr_area__in'] = area_list
    result_list = request.POST.getlist('result_list')
    if result_list:
        search_dict['opr_finance_reco_result__in'] = result_list

    #将3个查询条件进行或查询
    financereco_list = OprFinanceReco.objects.filter(**search_dict)

    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
        financereco_list, request)

    #获取模板内容
    content_html = render_to_string('operation/financereco_list.html',
                                    {'page_objects': page_objects, 'page_len': page_len, 'p':p,
                                     'show_first': show_first, 'show_end':show_end, 'end_page':end_page,
                                     'page_range':page_range, 'current_page':current_page})
    #组装返回结果
    result = {'flag': "success", 'msg': '', 'html': content_html}

    return JsonResponse(result)

#CMIOT账务稽核管理页面——下载处理方法
def cFinanceRecoDownload(request):
    #获取文件下载目录
    doanloaddir = config.get('Finance', 'finance_downloaddir')
    if not os.path.exists(doanloaddir):
        print(u'目录%s不存在，新建目录！' % doanloaddir)
        os.makedirs(doanloaddir)

    if request.method == 'POST':
        page = request.POST.get('page')
        id_list = request.POST.getlist('id_list')
        financeFileZip.delay(page=page, id_list=id_list)

        back_dic = {'existflag': "存在", 'existdes': "正在后台打包，请稍后！"}
        import json
        return HttpResponse(json.dumps(back_dic))

    elif request.method == 'GET':
        filename = request.GET.get('filename')
        id = request.GET.get('id')

        #通过文件名下载
        if filename:
            filepath = os.path.join(doanloaddir, filename)
            file = open(filepath, 'rb')

            response = FileResponse(file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{}"'.format(filename)
            return response
        #通过id下载
        elif id:
            financereco = OprFinanceReco.objects.get(opr_finance_reco_id=id)
            filename = financereco.opr_finance_reco_file
            filedir = financereco.opr_finance_reco_filedir
            filepath = os.path.join(filedir, filename)
            file = open(filepath, 'rb')

            response = FileResponse(file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{}"'.format(filename)
            return response
        #查询压缩包打包进度
        else:
            #获取全局变量
            percent = cache.get('percent')
            data = {'percent':percent}
            print(u'账务稽核文件打包完成进度 : %s' %percent + '%')
            if percent == 100:
                filename = cache.get('filename')
                data['filename']=filename
            return JsonResponse(data)

#CMIOT账务稽核管理页面——账务文件稽核处理方法
def cFinanceRecoAction(request):
    id_list = request.POST.getlist('id_list')
    print(id_list)
    try:
        reco_list = OprFinanceReco.objects.filter(opr_finance_reco_id__in=id_list)
        for reco in reco_list:
            reco.opr_finance_reco_result = '准备稽核'
            reco.opr_finance_opruser = request.session['user_name']
            reco.opr_finance_reco_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            reco.save()
        cFinanceRecoTask.delay()
        back_dic = {'existflag': "存在", 'existdes': "已生成稽核任务，正在后台执行，请稍后刷新页面查看稽核结果！"}
    except ObjectDoesNotExist:
        back_dic = {'existdes': "√选的省份未找到相关数据，请检查！"}
    import json
    return HttpResponse(json.dumps(back_dic))

