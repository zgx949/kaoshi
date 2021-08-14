import datetime
import json

import requests
from django.contrib import admin

from .models import *

admin.site.site_header = "建协批量考试系统"
admin.site.site_title = "建协批量考试系统"
admin.site.index_title = "建协批量考试系统"


# Register your models here.

class Question_bankAdmin(admin.ModelAdmin):
    list_display = ('classname', 'question', 'answer', 'option')
    search_fields = ('question',)
    list_filter = ('classname',)
    list_per_page = 50


class UserAdmin(admin.ModelAdmin):
    list_filter = ('classname', 'status', 'create_time')
    search_fields = ('id_card',)
    list_display = ('classname', 'icon', 'id_card', 'name', 'status', 'userid_score', 'create_time')
    actions = ('start', 'check_user')

    # def start(self, request, queryset):
    #     for i in queryset:
    #         # 交卷
    #         queryset.update(status=1, create_time=datetime.datetime.now())
    #         print(i.userid)
    #     pass
    #
    # start.short_description = '选中开始考试'
    # start.icon = 'fas fa-audio-description'
    def start(self, request, queryset):
        data_list = []
        for i in queryset:
            # 开始
            queryset.update(status=-2, create_time=datetime.datetime.now())
            data_list.append({'userid': i.userid, 'classname': str(i.classname)})
        print(requests.post(
            url='http://127.0.0.1:5000/',
            # url='http://192.168.1.6:5000/',
            data=json.dumps(data_list),
            headers={
                'Content-Type': 'application/json',
            }
        ).json())
        # get_ids(data_list)

    start.short_description = '选中开始'
    start.icon = 'fas fa-audio-description'

    def check_user(self, request, queryset):
        for i in queryset:
            try:
                datalist = requests.get(
                    url='https://api.ccenpx.com.cn/official/official_list',
                    # url='https://api.ccenpx.com.cn/official/official_score',
                    headers={
                        'Host': 'api.ccenpx.com.cn',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Referer': 'https://www.ccenpx.com.cn/',
                        'Origin': 'https://www.ccenpx.com.cn',
                        'Connection': 'keep-alive',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'no-cors',
                        'Sec-Fetch-Site': 'same-site',
                        'Pragma': 'no-cache',
                        'Cache-Control': 'no-cache',
                    },
                    params={
                        'page': '1',
                        'limit': '20',
                        'txt_userid': i.userid,
                    }
                ).json()['data']
                for data in datalist:
                    # if data['major_id'][:1] in str(i.classname):
                    if data['is_pass'] == 1:
                        User.objects.filter(id=i.id).update(status=2)
                        break
                    else:
                        User.objects.filter(id=i.id).update(status=-1)
                        pass

            except:
                pass

    check_user.short_description = '选中检查账号'
    check_user.icon = 'fas fa-audio-description'


class CdkeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'cdk', 'user')
    actions = ('makcdks',)

    def makcdks(self, request, queryset):
        pass

    makcdks.short_description = '生成cdk'
    makcdks.icon = 'fas fa-audio-description'
    makcdks.action_type = 1
    makcdks.action_url = 'http://www.baidu.com'


admin.site.register(Question_bank, Question_bankAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Cdkey, CdkeyAdmin)
admin.site.register(Classname)
