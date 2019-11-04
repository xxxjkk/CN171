import datetime

from django.db import transaction, models
from django.http import HttpResponse
import xlwt,xlrd
from io import BytesIO

#主机信息的导出下载
from CN171_background.models import BgTaskManagement
from CN171_cmdb.models import HOST_STATUS, CmdbHost
from CN171_tools.common_api import get_tuple_key


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
                    bgTaskManagement_obj = BgTaskManagement.objects.get(bg_module=row_value[5],bg_domain=row_value[6])
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