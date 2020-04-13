import datetime
import string

from django.db import transaction, models
from django.http import HttpResponse
import xlwt,xlrd
from io import BytesIO

#主机信息的导出下载
from CN171_background.models import BgTaskManagement
from CN171_cmdb.models import HOST_STATUS, CmdbHost, CmdbAppCluster, CLUSTER_STATUS, APP_STATUS, CmdbAppNetmode, CmdbApp
from CN171_tools.common_api import get_tuple_key, isNullStr, toInt


#导出主机
def excel_export_host(list_obj):
    if list_obj:
        # 创建工作薄
        ws = xlwt.Workbook(encoding="utf-8")
        w = ws.add_sheet(u'主机信息')
        w.write(0, 0, 'id')
        w.write(0, 1, u'主机名')
        w.write(0, 2, u'主机类型')
        w.write(0, 3, u'资源池')
        w.write(0, 4, u'业务IP')
        w.write(0, 5, u'管理IP')
        w.write(0, 6, u'归属模块')
        w.write(0, 7, u'归属中心')
        w.write(0, 8, u'操作系统')
        w.write(0, 9, u'CPU')
        w.write(0, 10, u'内存')
        w.write(0, 11, u'本地磁盘')
        w.write(0, 12, u'外置磁盘')
        w.write(0, 13, u'录入时间')
        w.write(0, 14, u'主机状态')
        # 写入数据
        excel_row = 1
        for obj in list_obj:
            cmdb_host_id = obj.cmdb_host_id
            cmdb_host_name = obj.cmdb_host_name
            cmdb_host_type = obj.cmdb_host_type
            cmdb_host_pod = obj.cmdb_host_pod
            cmdb_host_busip = obj.cmdb_host_busip
            cmdb_host_manip = obj.cmdb_host_manip
            bg_module = obj.bg.bg_module
            bg_domain = obj.bg.bg_domain
            cmdb_host_system = obj.cmdb_host_system
            cmdb_host_cpu = obj.cmdb_host_cpu
            cmdb_host_RAM = obj.cmdb_host_RAM
            cmdb_host_local_disc = obj.cmdb_host_local_disc
            cmdb_host_outlay_disc = obj.cmdb_host_outlay_disc
            cmdb_host_insert_time = obj.cmdb_host_insert_time.strftime('%Y-%m-%d %H:%M:%S')
            # cmdb_host_status = obj.cmdb_host_status_choices  # 只显示数字
            cmdb_host_status = obj.get_cmdb_host_status_display()
            w.write(excel_row, 0, cmdb_host_id)
            w.write(excel_row, 1, cmdb_host_name)
            w.write(excel_row, 2, cmdb_host_type)
            w.write(excel_row, 3, cmdb_host_pod)
            w.write(excel_row, 4, cmdb_host_busip)
            w.write(excel_row, 5, cmdb_host_manip)
            w.write(excel_row, 6, bg_module)
            w.write(excel_row, 7, bg_domain)
            w.write(excel_row, 8, cmdb_host_system)
            w.write(excel_row, 9, cmdb_host_cpu)
            w.write(excel_row, 10, cmdb_host_RAM)
            w.write(excel_row, 11, cmdb_host_local_disc)
            w.write(excel_row, 12, cmdb_host_outlay_disc)
            w.write(excel_row, 13, cmdb_host_insert_time)
            w.write(excel_row, 14, cmdb_host_status)
            excel_row += 1
        sio = BytesIO()
        ws.save(sio)
        sio.seek(0)
        response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
        now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
        file_name = 'host_info_' + now + '.xls'
        response['Content-Disposition'] = 'attachment;filename=' + file_name
        response.write(sio.getvalue())
        return response

#主机信息的导入保存
def excel_import_host(file_obj):
    type_excel = file_obj.name.split('.')[1]
    if type_excel in ['xlsx', 'xls']:
        # 开始解析上传的excel表格
        wb = xlrd.open_workbook(filename=None, file_contents=file_obj.read())
        table = wb.sheets()[0]
        nrows = table.nrows  # 行数
        # ncole = table.ncols  # 列数
        try:
            # 正常的数据库操作应该是原子性操作
            with transaction.atomic():
                for i in range(1, nrows):
                    # i/o
                    row_value = table.row_values(i)  # 一行的数据
                    # 添加多对多字段
                    # 主要这里不能使用get，否则报错
                    bg_module = row_value[5]
                    bg_domain = str(row_value[6])
                    bgTaskManagement = BgTaskManagement.objects.filter(bg_module=bg_module,bg_domain=bg_domain)
                    bgTaskManagement_obj = bgTaskManagement[0]
                    # 生成主机对象，添加
                    cmdbHost_obj = CmdbHost.objects.create(
                        cmdb_host_name=row_value[0],
                        cmdb_host_type=row_value[1],
                        cmdb_host_pod=row_value[2],
                        cmdb_host_busip=row_value[3],
                        cmdb_host_manip=row_value[4],
                        bg=bgTaskManagement_obj,
                        cmdb_host_system=row_value[7],
                        cmdb_host_cpu=row_value[8],
                        cmdb_host_RAM=row_value[9],
                        cmdb_host_local_disc = row_value[10],
                        cmdb_host_outlay_disc = row_value[11],
                        cmdb_host_insert_time=datetime.datetime.now(),
                        cmdb_host_status = get_tuple_key(HOST_STATUS,row_value[13])
                    )
        except Exception as e:
            return '出现错误...%s' % e
            print(e)
        return "上传成功"
    else:
        return '上传文件格式不是xlsx或xls'


#主机信息的导入保存
def excel_import_app(file_obj):
    type_excel = file_obj.name.split('.')[1]
    if type_excel in ['xlsx', 'xls']:
        # 开始解析上传的excel表格
        wb = xlrd.open_workbook(filename=None, file_contents=file_obj.read())
        xl_sheet_names = wb.sheet_names()
        # 打印所有sheet页名称
        try:
            # 正常的数据库操作应该是原子性操作
            with transaction.atomic():
                for sheet_name in xl_sheet_names:
                    table=wb.sheet_by_name(sheet_name)
                    nrows = table.nrows  # 行数
                    # ncole = table.ncols  # 列数
                    if(table.ncols==4):
                        excel_opr_cluster(table,nrows)
                    else:
                        excel_opr_app(table,nrows)
        except Exception as e:
            return '出现错误...%s' % e
            print(e)
        return "上传成功"
    else:
        return '上传文件格式不是xlsx或xls'

#导入集群操作
def excel_opr_cluster(table,nrows):
    for i in range(1, nrows):
        # i/o
        row_value = table.row_values(i)  # 一行的数据
        # 添加多对多字段
        # 主要这里不能使用get，否则报错
        bgTaskManagement_obj = BgTaskManagement.objects.get(bg_module=row_value[1], bg_domain=str(row_value[2]))
        # 生成主机对象，添加
        cmdbApp_obj = CmdbAppCluster.objects.create(
            name=row_value[0],
            bgTaskManagement=bgTaskManagement_obj,
            cluster_status=get_tuple_key(CLUSTER_STATUS, row_value[3])
        )

#导入应用操作
def excel_opr_app(table,nrows):
    for i in range(1, nrows):
        # i/o
        row_value = table.row_values(i)  # 一行的数据
        # 添加多对多字段
        # 主要这里不能使用get，否则报错
        cmdb_host_obj=CmdbHost.objects.get(cmdb_host_name=row_value[1])
        appNetmode_obj = CmdbAppNetmode.objects.get(net_mode=row_value[2])
        cmdbAppCluster_obj=CmdbAppCluster.objects.get(name=row_value[3])
        # 生成主机对象，添加
        cmdbHost_obj = CmdbApp.objects.create(
            app_name=row_value[0],
            cmdb_host=cmdb_host_obj,
            appNetmode=appNetmode_obj,
            cmdbAppCluster=cmdbAppCluster_obj,
            app_insert_time=datetime.datetime.now(),
            app_status=get_tuple_key(APP_STATUS, row_value[4])
        )

#导出应用信息
def excel_export_app(list_cluster_obj):
    if list_cluster_obj:
        # 创建工作薄
        ws = xlwt.Workbook(encoding="utf-8")
        w = ws.add_sheet(u'应用信息')
        w.write(0, 0, u'网元名')
        w.write(0, 1, u'归属模块')
        w.write(0, 2, u'归属中心')
        w.write(0, 3, u'状态')
        # 写入数据
        excel_row = 1
        for cluster_obj in list_cluster_obj:
            cluster_id =cluster_obj.id
            cluster_name = cluster_obj.name
            cluster_bg_module = cluster_obj.bgTaskManagement.bg_module
            cluster_bg_domain = cluster_obj.bgTaskManagement.bg_domain
            cluster_status = cluster_obj.get_cluster_status_display()
            # cmdb_host_status = obj.cmdb_host_status_choices  # 只显示数字
            w.write(excel_row, 0, cluster_name)
            w.write(excel_row, 1, cluster_bg_module)
            w.write(excel_row, 2, cluster_bg_domain)
            w.write(excel_row, 3, cluster_status)
            excel_row += 1
            appListInCluster = cluster_obj.cmdbApp_cmdbAppCluster.all()
            if appListInCluster:
                w.write(excel_row, 0, "网元名")
                w.write(excel_row, 1, "业务IP")
                w.write(excel_row, 2, "管理IP")
                w.write(excel_row, 3, "所属模块")
                w.write(excel_row, 4, "所属中心")
                w.write(excel_row, 5, "状态")
                w.write(excel_row, 6, "操作系统")
                w.write(excel_row, 7, "CPU")
                w.write(excel_row, 8, "内存")
                w.write(excel_row, 9, "本地磁盘")
                w.write(excel_row, 10, "外置磁盘")
                w.write(excel_row, 11, "录入时间")
                excel_row += 1
                for app in appListInCluster:
                    app_name = app.app_name
                    cmdb_host_busip = app.cmdb_host.cmdb_host_busip
                    cmdb_host_manip = isNullStr(app.cmdb_host.cmdb_host_manip)
                    bg_module = app.cmdb_host.bg.bg_module
                    bg_domain = app.cmdb_host.bg.bg_domain
                    app_status = isNullStr(app.app_status)
                    cmdb_host_system = isNullStr(app.cmdb_host.cmdb_host_system)
                    cmdb_host_cpu = isNullStr(app.cmdb_host.cmdb_host_cpu)
                    cmdb_host_RAM = isNullStr(app.cmdb_host.cmdb_host_RAM)
                    cmdb_host_local_disc = isNullStr(app.cmdb_host.cmdb_host_local_disc)
                    cmdb_host_outlay_disc = isNullStr(app.cmdb_host.cmdb_host_outlay_disc)
                    app_insert_time = app.app_insert_time.strftime("%Y-%m-%d %H:%M:%S")
                    # cmdb_host_status = obj.cmdb_host_status_choices  # 只显示数字
                    w.write(excel_row, 0, app_name)
                    w.write(excel_row, 1, cmdb_host_busip)
                    w.write(excel_row, 2, cmdb_host_manip)
                    w.write(excel_row, 3, bg_module)
                    w.write(excel_row, 4, bg_domain)
                    w.write(excel_row, 5, app_status)
                    w.write(excel_row, 6, cmdb_host_system)
                    w.write(excel_row, 7, cmdb_host_cpu)
                    w.write(excel_row, 8, cmdb_host_RAM)
                    w.write(excel_row, 9, cmdb_host_local_disc)
                    w.write(excel_row, 10, cmdb_host_outlay_disc)
                    w.write(excel_row, 11, app_insert_time)
                    excel_row += 1
        sio = BytesIO()
        ws.save(sio)
        sio.seek(0)
        response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
        now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
        file_name = 'cluster_app_info_' + now + '.xls'
        response['Content-Disposition'] = 'attachment;filename=' + file_name
        response.write(sio.getvalue())
        return response

