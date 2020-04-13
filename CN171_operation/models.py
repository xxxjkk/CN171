from django.db import models

# Create your models here.

class OprFinance(models.Model):
    # '''CMIOT账务文件管理表'''
    opr_finance_id = models.AutoField(u"账务id", primary_key=True)
    opr_area = models.CharField(u"区域/省份", max_length=32)
    opr_cycle = models.CharField(u"账期", max_length=8)
    opr_payment = models.IntegerField(u"缴费", null=True, blank=True, default=0)
    opr_ar_invoice_detail_owe = models.IntegerField(u"欠费", null=True, blank=True, default=0)
    opr_ar_adjustment = models.IntegerField(u"调账", null=True, blank=True, default=0)
    opr_ar_apply_detail = models.IntegerField(u"销账", null=True, blank=True, default=0)
    opr_cm_acct_balance = models.IntegerField(u"余额", null=True, blank=True, default=0)
    opr_bb_bill_charge_bonus = models.IntegerField(u"赠费", null=True, blank=True, default=0)
    opr_ar_invoice_detail_all = models.IntegerField(u"账单", null=True, blank=True, default=0)
    opr_bc_acct = models.IntegerField(u"账户", null=True, blank=True, default=0)
    opr_ar_writeoff = models.IntegerField(u"呆坏账", null=True, blank=True, default=0)
    opr_ar_hunglog = models.IntegerField(u"解挂账", null=True, blank=True, default=0)
    opr_ar_transfer = models.IntegerField(u"转账", null=True, blank=True, default=0)
    opr_ar_invoice_prorate = models.IntegerField(u"分摊", null=True, blank=True, default=0)
    opr_unifypayment = models.IntegerField(u"个人代付", null=True, blank=True, default=0)
    opr_check_result = models.CharField(u"校验结果", max_length=8)
    opr_file_iscomplete = models.CharField(u"文档是否齐全", max_length=8 ,null=True, blank=True, default='-')

    def __unicode__(self):
        return self.opr_finance_id

    def __str__(self):
        return "{},{},{}".format(self.opr_finance_id, self.opr_area, self.opr_cycle)

    @property
    def all_names(self):
        return self.file.all()

    class Meta:
        verbose_name = u'CMIOT账务文件管理表'
        verbose_name_plural = verbose_name
        ordering = ['-opr_cycle']
        db_table = "opr_finance"

class OprFinanceFiledetail(models.Model):
    # '''CMIOT账务文件详情表'''
    opr_finance_filedetail_id = models.AutoField(u"文件id", primary_key=True)
    opr_finance = models.ForeignKey(to="OprFinance", on_delete=models.CASCADE, null=True, related_name='file')
    opr_finance_filedetail_type = models.CharField(u"文件类型", max_length=12)
    opr_finance_filedetail_name = models.CharField(u"文件名", max_length=64)
    opr_finance_filedetail_lasttime = models.DateTimeField(u"上次更新时间", null=True, blank=True)
    opr_finance_filedetail_thistime = models.DateTimeField(u"本次更新时间")
    opr_finance_filedetail_createtime = models.DateTimeField(u"远端生成时间")
    opr_finance_filedetail_num = models.IntegerField(u"更新次数")
    opr_finance_filedetail_dir = models.CharField(u"文件存储地址", max_length=256, null=True, blank=True)
    opr_finance_filedetail_check = models.CharField(u"校验结果", max_length=8, null=True, blank=True)

    def __unicode__(self):
        return self.opr_finance_filedetail_id

    def __str__(self):
        return "{},{},{}".format(self.opr_finance_filedetail_id,
                                 self.opr_finance_filedetail_type,
                                 self.opr_finance_filedetail_name)

    class Meta:
        verbose_name = u'CMIOT账务文件详情表'
        verbose_name_plural = verbose_name
        ordering = ['opr_finance_filedetail_name']
        db_table = "opr_finance_filedetail"

class OprFinanceCheckDetail(models.Model):
    # '''CMIOT账务文件校验结果详情表'''
    opr_finance_checkdetail_id = models.AutoField(u"序号id", primary_key=True)
    opr_finance = models.ForeignKey(to="OprFinance", on_delete=models.CASCADE, null=True)
    opr_finance_checkdetail_desc = models.TextField(u"校验结果描述")

    def __unicode__(self):
        return self.opr_finance_checkdetail_id

    def __str__(self):
        return "{}".format(self.opr_finance_checkdetail_id)

    class Meta:
        verbose_name = u'CMIOT账务文件校验结果详情表'
        verbose_name_plural = verbose_name
        db_table = "opr_finance_checkdetail"


class OprFinanceReco(models.Model):
    # '''CMIOT账务稽核表'''
    opr_finance_reco_id = models.AutoField(u"稽核记录id", primary_key=True)
    opr_finance = models.ForeignKey(to="OprFinance", on_delete=models.CASCADE, null=True, related_name='reco')
    opr_finance_reco_result = models.CharField(u"稽核结果", max_length=8)
    opr_finance_opruser = models.CharField(u"稽核操作人员", max_length=56,null=True, blank=True, default='-')
    opr_finance_reco_time = models.DateTimeField(u"稽核操作时间", null=True, blank=True)
    opr_finance_reco_file = models.CharField(u"稽核结果文件", max_length=32)
    opr_finance_reco_filedir = models.CharField(u"稽核结果文件存储地址", max_length=256, null=True, blank=True)

    def __unicode__(self):
        return self.opr_finance_reco_id

    def __str__(self):
        return "{},{},{}".format(self.opr_finance_reco_id,
                                 self.opr_finance,
                                 self.opr_finance_reco_result)

    class Meta:
        verbose_name = u'CMIOT账务稽核表'
        verbose_name_plural = verbose_name
        ordering = ['-opr_finance_reco_id']
        db_table = "opr_finance_reco"


class OprFinanceUploadRecord(models.Model):
    # '''CMIOT账务文件上传记录表'''
    opr_finance_upload_id = models.AutoField(u"文件上传记录id", primary_key=True)
    opr_finance_upload_status = models.CharField(u"文件上传状态", max_length=8)
    opr_finance_upload_time = models.DateTimeField(u"文件上传时间", null=True, blank=True)
    opr_finance_upload_num = models.IntegerField(u"上传次数", null=True, blank=True, default=0)
    opr_finance_upload_list = models.TextField(u"上传文件清单", null=True, blank=True)
    opr_finance_upload_faillist = models.TextField(u"上传失败文件清单", null=True, blank=True)

    def __unicode__(self):
        return self.opr_finance_upload_id

    def __str__(self):
        return "{},{},{}".format(self.opr_finance_upload_id,
                                 self.opr_finance_upload_status,
                                 self.opr_finance_upload_time)

    class Meta:
        verbose_name = u'CMIOT账务文件上传记录表'
        verbose_name_plural = verbose_name
        ordering = ['-opr_finance_upload_id']
        db_table = "opr_finance_uploadrecord"