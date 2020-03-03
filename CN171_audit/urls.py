from django.urls import path
from django.conf.urls import include,url
from CN171_audit import views as auditViews

urlpatterns = [

    url(r'^information/', auditViews.infoManagement, name='information'),
    url(r'^informationAdd/', auditViews.staffAdd, name='informationAdd'),
    url(r'^informationMod/(?P<staff_id>\d+)/$', auditViews.staffMod, name='informationMod'),
    url(r'^informationDel/', auditViews.staffDel, name='informationDel'),
    url(r'^importStaffInfo/', auditViews.importStaffInfo, name='importStaffInfo'),
    url(r'^exportStaffInfo/', auditViews.exportStaffInfo, name='exportStaffInfo'),
    url(r'^staffSearch/', auditViews.staffSearch, name='staffSearch'),
    url(r'^accountAudit/', auditViews.accountAudit, name='accountAudit'),

]
