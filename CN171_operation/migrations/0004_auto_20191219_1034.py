# Generated by Django 2.2.5 on 2019-12-19 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CN171_operation', '0003_auto_20191218_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='oprfinancefiledetail',
            name='opr_finance_filedetail_check',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='校验结果'),
        ),
        migrations.AddField(
            model_name='oprfinancefiledetail',
            name='opr_finance_filedetail_createtime',
            field=models.DateTimeField(default='2019-12-18 14:13:26', verbose_name='远端生成时间'),
            preserve_default=False,
        ),
    ]