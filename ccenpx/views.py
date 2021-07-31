import json
from urllib import parse
import requests
from django.http import HttpResponse
import re
from fuzzywuzzy import fuzz
from django.shortcuts import render

# Create your views here.
from ccenpx.models import Question_bank, User, Classname


class Exam:

    def __init__(self, classname, likes):
        if len(classname) > 2:
            classname = classname[:1]
        self.classname = classname
        if classname == '通用':
            self.banks = Question_bank.objects.all()
        else:
            self.banks = Question_bank.objects.filter(classname__contains=classname)
        # self.banks = Question_bank.objects.all()
        self.likes = int(likes)

    def get_ans(self, question):
        for bank in self.banks:
            if fuzz.ratio(bank.question, question) > self.likes:
                return {'question': bank.question, 'options': bank.option.replace(',', '').replace(' ', '')}
        return {'question': None, 'options': None}


def makebank(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            classname = json_data['classname']
            text = json_data['text']
            for question, options in re.findall(r'题：(.*?)\s答案：([A-Z]*)', text):
                Question_bank.objects.create(
                    classname=classname,
                    question=question,
                    option=options
                )

            return HttpResponse(json.dumps({'msg': 'ok', 'code': 1}), content_type="application/json")

        except Exception as e:
            return HttpResponse(json.dumps({'msg': str(e), 'code': -1}), content_type="application/json")
    else:
        try:
            classname = request.GET.get('classname')
            question = request.GET.get('question')
            options = request.GET.get('options')

            Question_bank.objects.create(
                classname=classname,
                question=question,
                option=options
            )
            return HttpResponse(json.dumps({'msg': 'ok', 'code': 1}), content_type="application/json")
        except Exception as e:
            return HttpResponse(json.dumps({'msg': str(e), 'code': -1}), content_type="application/json")


def ans(request):
    exam = Exam(request.GET.get('classname'), request.GET.get('likes'))

    return HttpResponse(json.dumps(exam.get_ans(request.GET.get('question'))), content_type='application/json')


def score(request):
    # respon = requests.post(
    #     url='https://api.ccenpx.com.cn/official/official_list',
    #     headers={
    #             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    #             'Accept': 'application/json, text/javascript, */*; q=0.01',
    #             'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    #             'Origin': 'https://www.ccenpx.com.cn',
    #             'Connection': 'keep-alive',
    #             'Referer': 'https://www.ccenpx.com.cn/',
    #             'Sec-Fetch-Dest': 'empty',
    #             'Sec-Fetch-Mode': 'cors',
    #             'Sec-Fetch-Site': 'same-site',
    #         },
    #     params={
    #         'page': '1',
    #         'limit': '20',
    #         'txt_userid': request.GET.get('userid')
    #     }
    # )

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Referer': 'https://www.ccenpx.com.cn/',
        'Origin': 'https://www.ccenpx.com.cn',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-site',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    params = (
        ('page', '1'),
        ('limit', '20'),
        ('txt_userid', request.GET.get('userid')),
    )

    respon = requests.post('https://api.ccenpx.com.cn/official/official_list', headers=headers, params=params)
    return HttpResponse(
        respon.text,
        content_type='application/json'
    )


def login(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            data = ''
            for temp in json_data:
                data += temp + str(json_data[temp]) + '&'
            respon = requests.post(
                url='https://api.ccenpx.com.cn/login/login',
                # data=data[:-1],
                data='txt_username=510113198511100016&txt_password=0016&txt_type=1&txt_captcha=&txt_md5=0637d1e2d4e93b1c83cea6711488a162&txt_ic=300&txt_captcha_change=1',
                headers={
                    'Host': 'api.ccenpx.com.cn',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    # 'Content-Length': '146',
                    'Origin': 'https://www.ccenpx.com.cn',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.ccenpx.com.cn/',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-site',
                }
            )

            return HttpResponse(respon.text, content_type="application/json")

        except Exception as e:
            return HttpResponse(json.dumps({'msg': str(e), 'code': -1}), content_type="application/json")


def adduser(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            # classname = json_data['classname']
            cls_id = Classname.objects.get(name='通用')
            id_card = json_data['id_card']
            name = json_data['name']
            icon_url = json_data['icon_url']
            userid = json_data['userid']
            User.objects.create(
                classname=cls_id,
                id_card=id_card,
                name=name,
                icon_url=icon_url,
                userid=userid,
                status=0
            )
            return HttpResponse(json.dumps({'msg': 'ok', 'code': 1}), content_type="application/json")
        except Exception as e:
            return HttpResponse(json.dumps({'msg': str(e), 'code': -1}), content_type="application/json")

    else:
        return HttpResponse(json.dumps({'msg': 'method must be post', 'code': -1}), content_type="application/json")


def updatestatus(request):
    try:
        if request.method == 'GET':
            classname = request.GET.get('classname')
            # cls_id = Classname.objects.get(name=classname)
            cls_id = Classname.objects.get(name='通用')
            userid = request.GET.get('userid')
            status = int(request.GET.get('status'))
            person = User.objects.filter(userid=userid, classname=cls_id)
            person.update(status=status)
            return HttpResponse(json.dumps({'msg': 'ok', 'code': 1}), content_type="application/json")
    except:
        return HttpResponse(json.dumps({'msg': 'method must be get', 'code': -1}), content_type="application/json")
