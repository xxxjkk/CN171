from django.conf.urls import include,url
from CN171_cmdb import views as cmdbviews
from CN171_cmdb import tasks

urlpatterns = [

    #cmdb主页面
    #url(r'^cmdb/', cmdbviews.cmdbIndex, name='cmdb'),
    #主机管理
    url(r'^host_management/', cmdbviews.hostManagement, name='hostManagement'),
    url(r'^host_detail/',cmdbviews.hostDetail,name='hostDetail'),
    url(r'^host_del/',cmdbviews.hostDel,name='hostDel'),
    url(r'^batchRefreshHostStatusInfo/',cmdbviews.batchRefreshHostStatusInfo,name='batchRefreshHostStatusInfo'),
    url(r'^export_host_info/',cmdbviews.export_host_info,name='export_host_info'),
    url(r'^import_host_info/',cmdbviews.import_host_info,name='import_host_info'),

    #主机密码管理
    url(r'^host_pwd_opr_log_page/', cmdbviews.hostPwdOprLogPage, name='hostPwdOprLogPage'),
    url(r'^host_pwd_opr_log/', cmdbviews.hostPwdOprLog, name='hostPwdOprLog'),
    url(r'^host_pwd_detail_log/', cmdbviews.hostPwdDetailLog, name = 'hostPwdDetailLog'),
    url(r'^host_pwd_edit_page/',cmdbviews.redEditHostPwdPage, name='redEditHostPwdPage'),
    url(r'^host_pwd_edit/',cmdbviews.editHostPwd, name='editHostPwd'),
    url(r'^host_add_page/',cmdbviews.hostAddPage,name='hostAddPage'),

    #应用管理
    url(r'^app_management/', cmdbviews.appManagement, name='appManagement'),
    url(r'^find_apps_in_cluster/', cmdbviews.findAppsInCluster, name='findAppsInCluster'),
    url(r'^cluster_app_detail/',cmdbviews.clusterAppDetail, name='clusterAppDetail'),

]
