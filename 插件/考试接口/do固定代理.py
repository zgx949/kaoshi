import time
import hashlib
import requests
import threadpool
import re
from requests.auth import HTTPProxyAuth
# from multiprocessing import Pool
from flask import Flask, request, jsonify

# server = '192.168.1.3:8000'
server = '127.0.0.1:8000'
app = Flask(__name__)

requests.packages.urllib3.disable_warnings()
# 个人中心获取orderno与secret
from requests.exceptions import ProxyError

auth = "1"

# proxy = {"https": "http://" + ip_port}


open_proxy = True


# from ccenpx.views import Exam


class Dopaper:
    def __init__(self, userid, majorid, placeid, paperid, classname, likes, proxy):
        """
        初始化
        :param userid: 用户id
        :param majorid: 考试类型
        :param placeid: 考试场次
        :param paperid: 试卷id
        :param classname: 检索答案分类
        :param likes: 匹配度
        """
        self.userid = userid
        self.majorid = majorid
        self.placeid = placeid
        self.paperid = paperid
        # self.exam = Exam(classname, likes)
        self.classname = classname
        self.likes = likes
        # topicid_list 还没获取
        self.dataid_list = []
        self.offical_id = ''
        self.proxy = proxy
        try:
            print(requests.get(url='http://' + server + '/status',
                               params={'classname': classname, 'userid': userid, 'status': 1}).json())
            try:
                dataids = self.get_question('')['data']['total']
            except:
                dataids = []
            for dataid in dataids:
                for item in dataids[dataid]['topic']:
                    if item['is_answer'] == 0:
                        self.dataid_list.append(item['id'])
        except:
            self.__init__(userid, majorid, placeid, paperid, classname, likes)

        ##############

    def answer_save(self, answer, topicid, dataid):
        """
        保存答案
        :param topicid: 类别id
        :param answer: 答案
        :param dataid: 题目id
        :return json_data: 返回的json
        """
        try:
            answer = answer.replace(',', '')
            if len(answer) > 1:
                temp_ans = answer
                answer = ''
                for option in temp_ans:
                    answer += option + ','
                answer = answer[:-1]
            url = r'https://api.ccenpx.com.cn/official/official_save'
            data = {'txt_userid': self.userid,
                    'txt_majorid': self.majorid,
                    'txt_placeid': self.placeid,
                    'txt_paperid': self.paperid,
                    'txt_dataid': dataid,
                    'txt_topicid': topicid,
                    'txt_answers': answer,
                    }
            headers = {
                "Authorization": auth,
                'Host': 'api.ccenpx.com.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://www.ccenpx.com.cn',
                'Connection': 'keep-alive',
                'Referer': 'https://www.ccenpx.com.cn/',
                'Cache-Control': 'max-age=0',
            }
            params = {'uuuid': self.userid}
            try:
                if open_proxy:
                    return requests.post(url=url, params=params, data=data, headers=headers, proxies=self.proxy,
                                         verify=False,
                                         allow_redirects=False).json()

                return requests.post(url=url, data=data, headers=headers).json()
            except:
                return self.answer_save(answer, topicid, dataid)
        except:
            print('正在重新提交答案')
            return self.answer_save(answer, topicid, dataid)

    def get_answer(self, question):
        """
        获取答案
        :param question:
        :return:
        """
        return requests.get('http://' + server + '/ans',
                            params={'question': question, 'classname': self.classname, 'likes': self.likes}).json()[
            'options']

    def get_question(self, dataid):
        """
        获取题目
        :return json_data: 返回的json
        """
        try:
            url = r'https://api.ccenpx.com.cn/official/official_topic'
            params = {'uuid': self.userid}
            data = {'txt_userid': self.userid,
                    'txt_majorid': self.majorid,
                    'txt_placeid': self.placeid,
                    'txt_paperid': self.paperid,
                    'txt_type': '1',
                    'txt_dataid': dataid,
                    }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
                'Host': 'api.ccenpx.com.cn',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Referer': 'https://www.ccenpx.com.cn/',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://www.ccenpx.com.cn',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0, no-cache',
                'Pragma': 'no-cache',
            }
            try:
                if open_proxy:
                    respon = requests.post(url=url, params=params, data=data, headers=headers, proxies=self.proxy,
                                           verify=False,
                                           allow_redirects=False)
                    if respon:
                        json_data = respon.json()
                else:
                    json_data = requests.post(url=url, data=data, headers=headers).json()
            except Exception as e:
                print('代理错误', e)
                return self.get_question(dataid)

            if '请稍后再试' in str(json_data):
                return self.get_question(dataid)

            try:
                dataid = json_data['data']['data_id']
            except TypeError:
                if "登陆超时" in str(json_data) or '结束' in str(json_data):
                    print(str(json_data))
                    print(requests.get(url='http://' + server + '/status',
                                       params={'classname': self.classname, 'userid': self.userid,
                                               'status': -1}).json())
                    return json_data

                print(str(json_data) + '\n正在重新请求...')
                return self.get_question(dataid)
            self.offical_id = json_data['data']['official_id']
            return json_data
        except:
            return self.get_question(dataid)

    def check(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.ccenpx.com.cn',
            'Connection': 'keep-alive',
            'Referer': 'https://www.ccenpx.com.cn/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        }

        data = {
            'txt_userid': self.userid,
            'txt_majorid': self.majorid,
            'txt_placeid': self.placeid,
            'txt_paperid': self.paperid,
            'txt_officialid': self.offical_id
        }

        response = requests.post('https://api.ccenpx.com.cn/official/official_score', headers=headers, data=data)
        try:
            return response.json()
        except:
            return self.check()

    def submit(self):
        """
        提交
        :return:
        """
        try:
            url = 'https://api.ccenpx.com.cn/official/official_score'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://www.ccenpx.com.cn',
                'Connection': 'keep-alive',
                'Referer': 'https://www.ccenpx.com.cn/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
            }
            data = {"txt_userid": self.userid, "txt_majorid": self.majorid,
                    "txt_placeid": self.placeid, "txt_paperid": self.paperid,
                    "txt_officialid": self.offical_id, "txt_is_finsish": 1}
            if open_proxy:
                respon = requests.post(url=url, data=data, headers=headers, proxies=self.proxy, verify=False,
                                       allow_redirects=False)
            else:
                respon = requests.post(url=url, data=data, headers=headers)
            if respon:
                json_data = respon.json()
                if json_data['code'] == 0:
                    res_json = self.check()
                    try:
                        if res_json['data']['is_pass'] == 1:
                            print(requests.get(url='http://' + server + '/status',
                                               params={'classname': self.classname, 'userid': self.userid,
                                                       'status': 2}).json())

                            requests.get()
                            print("已经通过")
                            return "已经通过"
                        else:
                            print(requests.get(url='http://' + server + '/status',
                                               params={'classname': self.classname, 'userid': self.userid,
                                                       'status': -1}).json())
                            print("挂科")
                            return "挂科"
                    except:
                        print(requests.get(url='http://' + server + '/status',
                                           params={'classname': self.classname, 'userid': self.userid,
                                                   'status': -1}).json())
                        return "异常"

                else:
                    print(requests.get(url='http://' + server + '/status',
                                       params={'classname': self.classname, 'userid': self.userid,
                                               'status': -1}).json())
                    return "异常"
            else:
                print(requests.get(url='http://' + server + '/status',
                                   params={'classname': self.classname, 'userid': self.userid, 'status': -1}).json())
                return "异常"

        except:
            return self.submit()


def get_proxy():
    url = 'http://tiqu.pyhttp.taolop.com/getip?count=1&neek=8545&type=1&yys=0&port=1&sb=&mr=1&sep=1&time=3'
    text = requests.get(url=url).text
    return 'http://' + text.replace('\r', '').replace('\n', '')


def startexam(data_list_object):
    """
    开始考试
    :param data_list_object:
    :return:
    """
    # 获取考试信息
    proxiy = {}
    try:

        userid = data_list_object['userid']

        proxiy = {"https": get_proxy()}
        classname = data_list_object['classname']
        headers = {
            'Host': 'api.ccenpx.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.ccenpx.com.cn',
            'Connection': 'keep-alive',
            'Referer': 'https://www.ccenpx.com.cn/',
            'Cache-Control': 'max-age=0',
        }

        if open_proxy:

            try:
                exam_data = requests.post(url='https://api.ccenpx.com.cn/official/official_major',
                                          headers=headers,
                                          data={
                                              'txt_userid': userid,
                                          })
            except Exception as e:
                print(e)
                return startexam(data_list_object)
        else:
            exam_data = requests.post(url='https://api.ccenpx.com.cn/official/official_major',
                                      headers=headers,
                                      data={
                                          'txt_userid': userid,
                                      })

        majorid = ''
        placeid = ''
        if exam_data:
            for item in exam_data.json()['data']:
                if item['flag'] == 1:
                    continue
                majorid = item['majorid']
                placeid = item['placeid']
                classname = item['name'].replace('员', '')[:2]

                if open_proxy:
                    try:
                        paper_data = requests.post('https://api.ccenpx.com.cn/official/official_home',
                                                   headers=headers,
                                                   data={
                                                       'txt_userid': userid,
                                                       'txt_majorid': majorid,
                                                       'txt_placeid': placeid,
                                                       'txt_paperid': ''
                                                   })
                    except Exception as e:
                        print(e)
                        return startexam(data_list_object)

                else:
                    paper_data = requests.post('https://api.ccenpx.com.cn/official/official_home',
                                               headers=headers,
                                               data={
                                                   'txt_userid': userid,
                                                   'txt_majorid': majorid,
                                                   'txt_placeid': placeid,
                                                   'txt_paperid': ''
                                               })
                if paper_data:
                    paperid = paper_data.json()['data']['paperid']
                    majorid = paper_data.json()['data']['majorid']
                    placeid = paper_data.json()['data']['placeid']
                    classname = paper_data.json()['data']['major']

                person = Dopaper(userid, majorid, placeid, paperid, classname, 90, proxiy)

                for data_id in person.dataid_list:
                    # time.sleep(1)
                    json_question = person.get_question(data_id)
                    topic_id = json_question['data']['topic_id']  # 获取topicid
                    content = json_question['data']['content']  # 获取题目正文
                    print(content)

                    options = person.get_answer(content)  # 查找答案
                    if options:

                        result_json = person.answer_save(options, topic_id, data_id)
                        print(options)
                    else:
                        result_json = person.answer_save('A', topic_id, data_id)
                        print('放空')
                person.submit()
                return ''
    except:
        requests.get(url='http://' + server + '/status',
                     params={'classname': person.classname, 'userid': person.userid, 'status': -1}).json()
        print('有账号出现异常正在重新考试...')
        startexam(data_list_object)
        return ''


pool = threadpool.ThreadPool(1)


def get_ids(data_list):
    # threadnum = 5
    # if len(data_list) < 5:
    #     threadnum = len(data_list)

    # pool = Pool(threadnum)
    # pool.map_async(startexam, data_list)

    requests = threadpool.makeRequests(startexam, data_list)
    [pool.putRequest(req) for req in requests]

    pool.wait()

    # start_do = threadpool.makeRequests(startexam, data_list)
    # [pool.putRequest(req) for req in start_do]
    # pool.wait()


@app.route("/", methods=["POST"])
def text_post():
    # 请求JSON格式
    my_json = request.get_json()
    # print(my_json)
    # get_name = my_json.get("name")  # 返回name参数
    # get_age = my_json.get("age")
    get_ids(my_json)
    return jsonify(msg='ok', len=len(my_json))  # 返回JSON格式


@app.route("/do", methods=["POST"])
def do_paper():
    my_json = request.get_json()
    userid = my_json['userid']
    majorid = my_json['majorid']
    placeid = my_json['placeid']
    paperid = my_json['paperid']
    classname = my_json['classname']
    person = Dopaper(userid, majorid, placeid, paperid, classname, 90)
    try:
        for data_id in person.dataid_list:
            json_question = person.get_question(data_id)
            topic_id = json_question['data']['topic_id']  # 获取topicid
            content = json_question['data']['content']  # 获取题目正文
            print(content)

            options = person.get_answer(content)  # 查找答案
            if options:

                result_json = person.answer_save(options, topic_id, data_id)
                print(options)
            else:
                result_json = person.answer_save('A', topic_id, data_id)
                print('放空')
        person.submit()
        return ''
    except:
        print('半自动账号有错误')
        return ''


if __name__ == '__main__':
    # startexam({'userid':"7f697YUCwYra9ry44odJCKFB9vm13A2DPdugKyVj4lyBp4c/366729",'classname':'施工员汇总'})
    app.run()  # 运行
    app.run(host='192.168.1.6', port=5000)  # 放在服务器,设置任何主机都能访问

# if __name__ == '__main__':
#     nowtime = time.time()
#     startexam('87a2EDGxCc9+aOnPPnCn6blWtAntkfu2OAnWQk93FpOJi7Q/370235', '安全、标准、材料、资料、监理员')
#     print(time.time() - nowtime)
