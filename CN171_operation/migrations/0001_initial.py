# Generated by Django 2.2.5 on 2019-12-09 10:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OprFinance',
            fields=[
                ('opr_finance_id', models.AutoField(primary_key=True, serialize=False, verbose_name='账务id')),
                ('opr_area', models.CharField(max_length=32, verbose_name='区域/省份')),
                ('opr_cycle', models.CharField(max_length=8, verbose_name='账期')),
                ('opr_payment', models.IntegerField(verbose_name='缴费')),
                ('opr_ar_invoice_detail_owe', models.IntegerField(verbose_name='欠费')),
                ('opr_ar_adjustment', models.IntegerField(verbose_name='调账')),
                ('opr_ar_apply_detail', models.IntegerField(verbose_name='销账')),
                ('opr_cm_acct_balance', models.IntegerField(verbose_name='余额')),
                ('opr_bb_bill_charge_bonus', models.IntegerField(verbose_name='赠费')),
                ('opr_ar_invoice_detail', models.IntegerField(verbose_name='账单')),
                ('opr_bc_acc', models.IntegerField(verbose_name='账户')),
                ('opr_ar_writeoff', models.IntegerField(verbose_name='呆坏账')),
                ('opr_ar_hunglog', models.IntegerField(verbose_name='解挂账')),
                ('opr_ar_transfer', models.IntegerField(verbose_name='转账')),
                ('opr_check_result', models.CharField(max_length=8, verbose_name='校验结果')),
                ('opr_reco_time', models.DateTimeField(verbose_name='最后稽核操作时间')),
            ],
            options={
                'verbose_name': 'CMIOT账务文件管理表',
                'verbose_name_plural': 'CMIOT账务文件管理表',
                'db_table': 'opr_finance',
                'ordering': ['-opr_finance_id', 'opr_area'],
            },
        ),
        migrations.CreateModel(
            name='OprFinanceFiledetail',
            fields=[
                ('opr_finance_filedetail_id', models.AutoField(primary_key=True, serialize=False, verbose_name='文件id')),
                ('opr_finance_filedetail_type', models.CharField(max_length=12, verbose_name='文件类型')),
                ('opr_finance_filedetail_name', models.CharField(max_length=64, verbose_name='文件名')),
                ('opr_finance_filedetail_lasttime', models.DateTimeField(verbose_name='上次更新时间')),
                ('opr_finance_filedetail_thistime', models.DateTimeField(verbose_name='本次更新时间')),
                ('opr_finance_filedetail_num', models.IntegerField(verbose_name='更新次数')),
                ('opr_finance_filedetail_dir', models.CharField(max_length=128, verbose_name='文件存储地址')),
                ('opr_finance_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='CN171_operation.OprFinance')),
            ],
            options={
                'verbose_name': 'CMIOT账务文件详情表',
                'verbose_name_plural': 'CMIOT账务文件详情表',
                'db_table': 'opr_finance_filedetail',
                'ordering': ['opr_finance_filedetail_name'],
            },
        ),
        migrations.CreateModel(
            name='OprFinanceCheckDetail',
            fields=[
                ('opr_finance_checkdetail_id', models.AutoField(primary_key=True, serialize=False, verbose_name='序号id')),
                ('opr_finance_checkdetail_desc', models.TextField(verbose_name='校验结果描述')),
                ('opr_finance_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='CN171_operation.OprFinance')),
            ],
            options={
                'verbose_name': 'CMIOT账务文件校验结果详情表',
                'verbose_name_plural': 'CMIOT账务文件校验结果详情表',
                'db_table': 'opr_finance_checkdetail',
            },
        ),
    ]