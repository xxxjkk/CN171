from django.conf.urls import include,url
from CN171_background import views as backgroundviews

urlpatterns = [

    # 任务管理
    url(r'^task_management/', backgroundviews.taskManagement, name='taskManagement'),
    url(r'^taskExecuteOne/', backgroundviews.taskExecuteOne, name='taskExecuteOne'),
]
