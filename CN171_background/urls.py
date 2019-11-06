from django.conf.urls import url
from CN171_background import views as backgroundviews
from django.views import static
from django.conf import settings

urlpatterns = [

    # 任务管理
    url(r'^task_management/', backgroundviews.taskManagement, name='taskManagement'),
    url(r'^taskExecuteOne/', backgroundviews.taskExecuteOne, name='taskExecuteOne'),
    url(r'^batchTaskStart/', backgroundviews.batchTaskStart, name='batchTaskStart'),
    url(r'^taskEdit/(?P<bg_id>\d+)/$', backgroundviews.taskEdit, name='taskEdit'),
    url(r'^taskAdd/$', backgroundviews.taskAdd, name='taskAdd'),
    url(r'^taskDel/$', backgroundviews.taskDel, name='taskDel'),
    url(r'^batchTaskStop/', backgroundviews.batchTaskStop, name='batchTaskStop'),
    url(r'^batchTaskReboot/', backgroundviews.batchTaskReboot, name='batchTaskReboot'),
    url(r'^taskLogSearch/', backgroundviews.taskLogSearch, name='taskLogSearch'),
    url(r'^task_log/', backgroundviews.taskLog, name='taskLog'),
    url(r'^reLoad/', backgroundviews.reLoad, name='reLoad'),
    url(r'^taskLogDetail/', backgroundviews.taskLogDetail, name='taskLogDetail'),
    url(r'^downloadTaskLog/', backgroundviews.downloadTaskLog, name='downloadTaskLog'),
    url(r'^appDetailByMoDo/', backgroundviews.appDetailByMoDo, name='appDetailByMoDo'),

]
