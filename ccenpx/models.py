from django.db import models

# Create your models here.
from django.utils.html import format_html


class Question_bank(models.Model):
    classname = models.CharField(verbose_name='分类', max_length=255, null=False)
    question = models.CharField(verbose_name='题目', max_length=255, null=False)
    answer = models.CharField(verbose_name='答案', max_length=255, null=True, blank=True)
    option = models.CharField(verbose_name='选项', max_length=255, null=False)
    # create_time = models.DateTimeField(verbose_name='创建时间', auto_created=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = '题库'

    def __str__(self):
        return self.question


class Classname(models.Model):
    name = models.CharField(verbose_name='分类名称', max_length=255, null=False)

    def __str__(self):
        return self.name


class User(models.Model):
    status_choices = ((-2, '正在排队'), (-1, '异常'), (0, '未开始'), (1, '正在考试'), (2, '已合格'))

    classname = models.ForeignKey(Classname, verbose_name='分类', null=True, blank=True, on_delete=models.SET_NULL)
    id_card = models.CharField(verbose_name='身份证', max_length=255, null=False)
    name = models.CharField(verbose_name='姓名', max_length=255, null=True, blank=True)
    icon_url = models.CharField(verbose_name='头像', max_length=255, null=True, blank=True)
    userid = models.CharField(verbose_name='userId', max_length=255, null=True, blank=True)
    status = models.IntegerField(verbose_name='当前状态', null=True, blank=False, default=0, choices=status_choices)
    create_time = models.DateTimeField(verbose_name='上次操作时间', auto_now_add=True)

    def userid_score(self):
        if self.userid:
            return format_html(
                '<a href="/score?userid={}" target="_blank">{}</a>',
                self.userid,
                self.userid + '(点击查询成绩)'
            )
        else:
            return format_html(
                '<a href="/score?userid=" target="_blank">{}</a>',
                '(点击查询成绩)'
            )

    def icon(self):
        if self.icon_url:
            return format_html(
                '<img src="{}" width="80px" height="80px"/>',
                self.icon_url,
            )
        else:
            return format_html(
                '<img src="{}" width="80px" height="80px"/>',
                'https://img2.baidu.com/it/u=2165691866,2570924737&fm=26&fmt=auto&gp=0.jpg'
            )

    class Meta:
        verbose_name_plural = '用户表'

    def __str__(self):
        return str(self.id_card)


class Cdkey(models.Model):
    status_choices = ((0, '未使用'), (1, '已使用'))

    cdk = models.CharField(verbose_name='卡密', max_length=255, null=False)
    user = models.ForeignKey(User, verbose_name='使用人', null=True, blank=True, on_delete=models.SET_NULL)

    status = models.IntegerField(verbose_name='当前状态', null=True, blank=False, default=0)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_created=True)

    class Meta:
        verbose_name_plural = '卡密表'

    def __str__(self):
        return str(self.cdk)



