import datetime
from os.path import *
from django.http import HttpResponse

#导出txt文档
def export_txt(content1):
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    file_name = './download/txt/host_pwd_detail_log_' + now + '.txt'
    file = open(file_name, 'w')
    file.write(content1)
    file.close()
    # 获取上级目录绝对路径
    dir_path = dirname(dirname(abspath(__file__)))
    file_path=dir_path+"\download\\txt"
    return file_path

#导出并下载txt文件
def export_download_txt(content1):
        response = HttpResponse(content_type='text/plain')
        now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
        file_name = 'host_pwd_detail_log_' + now + '.txt'
        response['Content-Disposition'] = 'attachment;filename='+file_name
        contentArray=content1.split("\n")
        for contentRow in contentArray:
            #print(contentRow)
            response.write(contentRow)
            response.write("\r\n")
        return response

