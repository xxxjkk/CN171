from django.conf.urls import include,url
from CN171_cmdb import views as cmdbviews

urlpatterns = [

    #cmdb主页面
    url(r'^cmdb/', cmdbviews.cmdbIndex, name='cmdb'),

]
