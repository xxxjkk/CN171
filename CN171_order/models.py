from django.db import models

# Create your models here.


class PbossOrderStatus(models.Model):
    # '''PBOSS订单状态观察表'''
    order_id = models.AutoField(u"状态id", primary_key=True)
    order_area = models.CharField(u"区域/省份", max_length=32)
    order_starttime = models.DateTimeField(u"开始时间")
    order_endtime = models.DateTimeField(u"结束时间")
    order_createtime = models.DateTimeField(u"生成时间")
    order_finish = models.IntegerField(u"结束")
    order_cbbsfailed = models.IntegerField(u"计费反馈同步失败")
    order_startfailed = models.IntegerField(u"流程启动异常")
    order_cbbssyncing = models.IntegerField(u"同步计费中")
    order_syncfailed = models.IntegerField(u"发起同步失败")
    order_cbbssynced = models.IntegerField(u"已发送计费同步请求")
    order_completed = models.IntegerField(u"已竣工")
    order_pending = models.IntegerField(u"待施工处理")
    order_processing = models.IntegerField(u"施工处理中")
    order_cbbssyncpending = models.IntegerField(u"待同步计费")

    def __unicode__(self):
        return self.order_id

    class Meta:
        verbose_name = u'PBOSS订单状态观察表'
        verbose_name_plural = verbose_name
        ordering = ['-order_createtime','order_area']
        db_table = "order_pboss_status"


class PbossOrderNode(models.Model):
    # '''PBOSS订单节点观察表'''
    order_id = models.AutoField(u"状态id", primary_key=True)
    order_area = models.CharField(u"区域/省份", max_length=32)
    order_starttime = models.DateTimeField(u"开始时间")
    order_endtime = models.DateTimeField(u"结束时间")
    order_createtime = models.DateTimeField(u"生成时间")
    order_HLR = models.IntegerField(u"HLR")
    order_IOMP = models.IntegerField(u"运管平台")
    order_SMSGateway = models.IntegerField(u"业务网关")
    order_BOSSHub = models.IntegerField(u"一级BOSS枢纽")
    order_CBBS = models.IntegerField(u"内容计费")
    order_Complete = models.IntegerField(u"竣工")
    order_XCWS = models.IntegerField(u"行车卫士")
    order_PCRF = models.IntegerField(u"PCRF")
    order_SCP = models.IntegerField(u"SCP")
    order_POC = models.IntegerField(u"和对讲")
    order_TRSS = models.IntegerField(u"物漫平台")
    order_NumRecycle = models.IntegerField(u"号码回收")

    def __unicode__(self):
        return self.order_id

    class Meta:
        verbose_name = u'PBOSS订单节点观察表'
        verbose_name_plural = verbose_name
        ordering = ['-order_createtime','order_area']
        db_table = "order_pboss_node"

class PbossOrderRollback(models.Model):
    # '''PBOSS订单回退观察表'''
    order_id = models.AutoField(u"状态id", primary_key=True)
    order_area = models.CharField(u"区域/省份", max_length=32)
    order_starttime = models.DateTimeField(u"开始时间")
    order_endtime = models.DateTimeField(u"结束时间")
    order_createtime = models.DateTimeField(u"生成时间")
    order_type = models.IntegerField(u"类型")
    order_number = models.IntegerField(u"数量")
    order_rbdesc = models.CharField(u"回退描述", max_length=256)

    def __unicode__(self):
        return self.order_id

    class Meta:
        verbose_name = u'PBOSS订单回退观察表'
        verbose_name_plural = verbose_name
        ordering = ['-order_createtime','order_area']
        db_table = "order_pboss_rollback"

class PbossOrderRecord(models.Model):
    # '''PBOSS订单生成记录表'''
    record_id = models.AutoField(u"id", primary_key=True)
    record_type = models.CharField(u"类型", max_length=32)
    record_mode = models.CharField(u"生成方式", max_length=16)
    record_starttime = models.DateTimeField(u"开始时间")
    record_endtime = models.DateTimeField(u"结束时间")
    record_createtime = models.DateTimeField(u"生成时间")
    record_result = models.CharField(u"执行结果", max_length=16)
    record_filedir = models.TextField(u"文件地址")

    def __unicode__(self):
        return self.record_id

    class Meta:
        verbose_name = u'PBOSS订单生成记录表'
        verbose_name_plural = verbose_name
        ordering = ['-record_createtime']
        db_table = "order_pboss_record"