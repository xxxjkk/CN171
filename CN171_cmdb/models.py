from django.db import models
# Create your models here.
from CN171_background.models import BgTaskManagement

HOST_STATUS = (
    (str(1), u"正常"),
    (str(2), u"异常"),
    (str(3), u"停机"),
    (str(4), u"启动中"),
    )

CLUSTER_STATUS = (
    (str(1), u"正常"),
    (str(2), u"部分正常（满足最小集）"),
    (str(3), u"异常"),
    (str(4), u"停止"),
    )

APP_STATUS = (
    (str(1), u"正常"),
    (str(2), u"部分正常"),
    (str(3), u"停止"),
    (str(4), u"变更中"),
    )

class CmdbHost(models.Model):
    # ''' cmdb_host 表'''
    cmdb_host_id = models.AutoField(u"主机id", primary_key=True)
    bg = models.ForeignKey( BgTaskManagement, on_delete=models.CASCADE,verbose_name=u"后台id", null=True)
    cmdb_host_name = models.CharField(u"主机名", max_length=128, unique=True)
    cmdb_host_type = models.CharField(u"类型", max_length=128)
    cmdb_host_pod = models.CharField(u"资源池", max_length=30)
    cmdb_host_system = models.CharField(u"操作系统", max_length=128, null=True, blank=True)
    cmdb_host_busip = models.CharField(u"业务ip", max_length=56)
    cmdb_host_manip = models.CharField(u"管理ip", max_length=56, null=True, blank=True)
    cmdb_host_cpu = models.CharField(u"cpu", max_length=56, null=True, blank=True)
    cmdb_host_RAM = models.CharField(u"内存", max_length=56, null=True, blank=True)
    cmdb_host_local_disc = models.CharField(u"本地磁盘", max_length=56, null=True, blank=True)
    cmdb_host_outlay_disc = models.CharField(u"外置磁盘", max_length=56, null=True, blank=True)
    cmdb_host_status = models.CharField(u"主机状态", choices=HOST_STATUS, max_length=36, null=True, blank=True)
    cmdb_host_insert_time = models.DateTimeField(u"录入时间", auto_now_add=True)

    def __str__(self):
        return "主机名："+self.cmdb_host_name+"  业务ip："+self.cmdb_host_busip

    class Meta:
        verbose_name = '主机'
        verbose_name_plural = '主机'
        ordering =["-cmdb_host_insert_time"]
        db_table = "cmdb_host"


class CmdbApp(models.Model):
    # ''' cmdb_app 表'''
    app_id = models.AutoField(u"应用id", primary_key=True)
    cmdb_host = models.ForeignKey("CmdbHost", on_delete=models.CASCADE ,verbose_name=u"主机id")
    appNetmode = models.ForeignKey('CmdbAppNetmode', on_delete=models.SET_DEFAULT,default=999, verbose_name=u'组网类型')
    app_name = models.CharField(u"网元名", max_length=128)
    app_status = models.CharField(u"状态",choices=APP_STATUS ,max_length=36, null=True, blank=True)
    app_insert_time = models.DateTimeField(u"录入时间", auto_now_add=True)
    app_lastopr_user = models.CharField(u"最后一次操作人员", max_length=56, null=True, blank=True)
    app_lastopr_type = models.CharField(u"最后一次操作类型", max_length=32, null=True, blank=True)
    app_lastopr_time = models.DateTimeField(u"最后一次操作时间", null=True, blank=True)
    app_lastopr_result = models.CharField(u"最后一次操作结果", max_length=32, null=True, blank=True)

    #集群id非空  默认不集群  默认值999
    cmdbAppCluster = models.ForeignKey('CmdbAppCluster',related_name='cmdbApp_cmdbAppCluster', on_delete=models.SET_DEFAULT, default=999, verbose_name=u'集群类型')

    def __str__(self):
        return self.app_name

    class Meta:
        verbose_name = '应用'
        verbose_name_plural = '应用'
        ordering=['-app_insert_time']
        db_table = "cmdb_app"

class CmdbAppLog(models.Model):
    # '''后台管理日志表'''
    id = models.AutoField(u"日志id", primary_key=True)
    app_id = models.IntegerField(u"后台id", null=True, blank=True)
    app_operation_user = models.CharField(u"操作人员", max_length=56,null=True, blank=True)
    app_operation = models.CharField(u"操作类型", max_length=32,null=True, blank=True)
    app_opr_result = models.CharField(u"操作结果", max_length=32,null=True, blank=True)
    app_operation_time = models.DateTimeField(u"操作开始时间")
    app_operation_finish_time = models.DateTimeField(u"操作完成时间",null=True, blank=True)
    app_log_dir = models.CharField(u"详细日志", max_length=256,null=True, blank=True)


    def __str__(self):
        return "{},{},{}".format(self.app_id,
                                 self.app_operation,
                                 self.app_opr_result)

    class Meta:
        verbose_name = u'应用管理日志表'
        verbose_name_plural = verbose_name
        db_table = "cmdb_app_log"



class CmdbAppCluster(models.Model):
    #集群表
    id = models.AutoField(u'集群id', primary_key=True)
    # 后台管理ID，主要是模块+中心，当后台管理项删除，集群（虚拟概念）默认存在为999，不删除
    bgTaskManagement = models.ForeignKey('CN171_background.BgTaskManagement', on_delete=models.SET_DEFAULT,default=999)
    name=models.CharField(u'集群名称', max_length=56, unique=True)
    cluster_status = models.CharField(u"状态",choices=CLUSTER_STATUS, max_length=36, null=True, blank=True)

    def __str__(self):
        return '集群应用的name为：'+self.name

    class Meta:
        verbose_name = '应用集群'
        verbose_name_plural = '集群'
        ordering=['-id']
        db_table = 'cmdb_app_cluster'


class CmdbAppNetmode(models.Model):
    # ''' cmdb_app_netmode 表'''

    net_id = models.AutoField(u"组网id", primary_key=True)
    net_mode = models.CharField(u"组网类型", max_length=56, unique=True)

    def __str__(self):
        return self.net_mode

    class Meta:
        verbose_name = '组网'
        verbose_name_plural = '组网'
        ordering=['net_id']
        db_table = "cmdb_app_netmode"


class HostPwdOprLog(models.Model):
    id = models.BigAutoField(u"主机密码操作日志ID", primary_key=True)
    opr_user_name = models.CharField(u"操作的用户账号", max_length=128, null=True, blank=True)
    modified_host_user = models.CharField(u"被修改的主机用户", max_length=128, null=True, blank=True)
    opr_result = models.CharField(u"操作结果", max_length=36, null=True, blank=True)
    opr_time = models.DateTimeField(u"操作时间", auto_now_add=True)
    detail_log = models.TextField(u"详细日志")

    def __str__(self):
        return self.modified_host_user

    def getDetailLog(self):
        return self.detail_log

    def getDetailLogId(self):
        return self.id

    def opr_log_save(self, opr_user_name,modified_host_user,opr_result,opr_time,detail_log):
        self.opr_user_name=opr_user_name
        self.modified_host_user=modified_host_user
        self.opr_result=opr_result
        self.opr_time=opr_time
        self.detail_log=detail_log
        self.save()

    class Meta:
        verbose_name = "主机密码操作日志"
        ordering = ['-opr_time']
        db_table ="cmdb_host_pwd_opr_log"


class AppCluster(object):
    pass


# 存储管理
class CmdbStorage(models.Model):
    # ''' cmdb_storage 表'''
    storage_id = models.AutoField(u"存储id", primary_key=True)
    cmdbStorageTotal = models.ForeignKey("CmdbStorageTotal", on_delete=models.CASCADE ,verbose_name=u"总存储")
    storage_name = models.CharField(u"存储项目名", max_length=128)
    storage_used = models.CharField(u"使用存储量",choices=APP_STATUS ,max_length=36, null=True, blank=True)
    storage_insert_time = models.DateTimeField(u"录入时间", auto_now_add=True)
    storage_type = models.CharField(u"存储类型", max_length=32, null=True, blank=True)

    def __str__(self):
        return self.storage_name

    class Meta:
        verbose_name = '存储'
        verbose_name_plural = '存储'
        ordering=['-storage_insert_time']
        db_table = "cmdb_storage"

 #总存储表
class cmdbStorageTotal(models.Model):
    # ''' cmdb_storage_total 表'''

    id = models.AutoField(u"总存储id", primary_key=True)
    storage_total = models.CharField(u"总存储", max_length=128)
    storage_left = models.CharField(u"剩余存储", max_length=56)
    storage_used = models.CharField(u"使用存储", max_length=56)
    storage_total_name = models.CharField(u"总存储名", max_length=128)

    def __str__(self):
        return self.storage_total

    class Meta:
        verbose_name = '总存储表'
        verbose_name_plural = '总存储表'
        ordering=['id']
        db_table = "cmdb_storage_total"