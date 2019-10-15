from django.conf.urls import include,url
from CN171_cmdb import views as cmdbviews

urlpatterns = [

    #cmdb主页面
    #url(r'^cmdb/', cmdbviews.cmdbIndex, name='cmdb'),
    url(r'^host_management/', cmdbviews.hostManagement, name='hostManagement'),
    url(r'^app_management/', cmdbviews.appManagement, name='appManagement'),
    url(r'^host_pwd_opr_log_page/', cmdbviews.hostPwdOprLogPage, name='hostPwdOprLogPage'),
    url(r'^host_pwd_opr_log/', cmdbviews.hostPwdOprLog, name='hostPwdOprLog'),
    url(r'^host_pwd_detail_log/', cmdbviews.hostPwdDetailLog, name = 'hostPwdDetailLog'),
    url(r'^host_pwd_edit_page/',cmdbviews.redEditHostPwdPage, name='redEditHostPwdPage'),
    url(r'^host_pwd_edit/',cmdbviews.editHostPwd, name='editHostPwd'),


]
