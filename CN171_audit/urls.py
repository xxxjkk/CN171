from django.urls import path
from django.conf.urls import url
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
    url(r'^systemAdd/', auditViews.systemAdd, name='systemAdd'),
    url(r'^systemDel/', auditViews.systemDel, name='systemDel'),
    url(r'^download/(?P<file_id>\d+)/$', auditViews.download, name='download'),
    url(r'^upload/(?P<file_id>\d+)/$', auditViews.upload, name='upload'),
    url(r'^accountAuditing/', auditViews.accountAuditing, name='accountAuditing'),
    url(r'^exportAccountAuditResult/', auditViews.exportAccountAuditResult, name='exportAccountAuditResult'),
]
