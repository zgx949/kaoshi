import time
import hashlib
import requests
import multiprocessing
from flask import Flask, request, jsonify

app = Flask(__name__)

requests.packages.urllib3.disable_warnings()
# 个人中心获取orderno与secret
# orderno = "DT20210723081019C2jYMKsj"
from requests.exceptions import ProxyError

orderno = "DT20210723081019C2jYMKsj"
secret = "dd269a72fc9e6accf51e016b4d9ff70a"
ip = "dynamic.xiongmaodaili.com"
# 按量订单端口
port = "8088"
# 按并发订单端口
# port = "8089"

ip_port = ip + ":" + port

timestamp = str(int(time.time()))  # 计算时间戳
txt = ""
txt = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp

txt = txt.encode()

md5_string = hashlib.md5(txt).hexdigest()  # 计算sign
sign = md5_string.upper()  # 转换成大写

auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp + "&change=true"

proxy = {"https": "http://" + ip_port}


# from ccenpx.views import Exam


class Dopaper:
    def __init__(self, userid, majorid, placeid, paperid, classname, likes):
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
        self.status = requests.get(url='127.0.0.1:8000/status',
                                   params={'classname': classname, 'userid': userid, 'status': -2})
        dataids = self.get_question('0')['data']['total']
        for dataid in dataids:
            for item in dataids[dataid]['topic']:
                self.dataid_list.append(item['id'])

        ##############

    def answer_save(self, answer, topicid, dataid):
        """
        保存答案
        :param topicid: 类别id
        :param answer: 答案
        :param dataid: 题目id
        :return json_data: 返回的json
        """
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
        try:
            return requests.post(url=url, data=data, headers=headers, proxies=proxy, verify=False,
                                 allow_redirects=False).json()
        except:
            return self.answer_save(answer, topicid, dataid)

    def get_answer(self, question):
        """
        获取答案
        :param question:
        :return:
        """
        return requests.get('http://127.0.0.1:8000/ans',
                            params={'question': question, 'classname': self.classname, 'likes': self.likes}).json()[
            'options']

    def get_question(self, dataid):
        """
        获取题目
        :return json_data: 返回的json
        """
        url = r'https://api.ccenpx.com.cn/official/official_topic'
        data = {'txt_userid': self.userid,
                'txt_majorid': self.majorid,
                'txt_placeid': self.placeid,
                'txt_paperid': self.paperid,
                'txt_type': '1',
                'txt_dataid': dataid,
                }
        headers = {
            "Authorization": auth,
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

            json_data = requests.post(url=url, data=data, headers=headers, proxies=proxy, verify=False,
                                      allow_redirects=False).json()
        except ProxyError:
            return self.get_question(dataid)

        if '请稍后再试' in str(json_data):
            return self.get_question(dataid)

        try:
            dataid = json_data['data']['data_id']
        except TypeError:
            print(str(json_data) + '\n正在重新请求...')
            return self.get_question(dataid)
        self.offical_id = json_data['data']['official_id']
        return json_data

    def submit(self):
        """
        提交
        :return:
        """
        url = 'https://api.ccenpx.com.cn/official/official_score'
        headers = {
            "Authorization": auth,
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
        respon = requests.post(url=url, data=data, headers=headers, proxies=proxy, verify=False, allow_redirects=False)
        if respon:
            json_data = respon.json()
            if json_data['code'] == 0:
                self.status = requests.get(url='127.0.0.1:8000/status',
                                           params={'classname': self.classname, 'userid': self.userid, 'status': 2})
                return "已经通过"
            else:
                self.status = requests.get(url='127.0.0.1:8000/status',
                                           params={'classname': self.classname, 'userid': self.userid, 'status': -1})
                return "挂科"
        else:
            self.status = requests.get(url='127.0.0.1:8000/status',
                                       params={'classname': self.classname, 'userid': self.userid, 'status': -1})
            return "异常"


def startexam(data_list_object):
    """
    开始考试
    :param data_list_object:
    :return:
    """
    # 获取考试信息
    userid = data_list_object['userid']
    classname = data_list_object['classname']
    headers = {
        "Authorization": auth,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
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
    exam_data = requests.post(url='https://api.ccenpx.com.cn/official/official_major',
                              headers=headers,
                              data={
                                  'txt_userid': userid,
                              }, proxies=proxy, verify=False, allow_redirects=False)
    majorid = ''
    placeid = ''
    if exam_data:
        for item in exam_data.json()['data']:
            if item['name'].replace('员', '')[:1] in classname:
                majorid = item['majorid']
                placeid = item['placeid']
                break

    paperid = ''
    paper_data = requests.post('https://api.ccenpx.com.cn/official/official_home',
                               headers=headers,
                               data={
                                   'txt_userid': userid,
                                   'txt_majorid': majorid,
                                   'txt_placeid': placeid,
                                   'txt_paperid': ''
                               }, proxies=proxy, verify=False, allow_redirects=False)
    if paper_data:
        paperid = paper_data.json()['data']['paperid']
    person = Dopaper(userid, majorid, placeid, paperid, classname, 90)

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
            print('放空')
    person.submit()


def get_ids(data_list):
    threadnum = 10
    if len(data_list) < 10:
        threadnum = len(data_list)

    mypool = multiprocessing.Pool(threadnum)
    for item in data_list:
        mypool.apply_async(startexam, (item,))

    mypool.close()
    mypool.join()
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


if __name__ == '__main__':
    app.run()  # 运行
    app.run(host="0.0.0.0")  # 放在服务器,设置任何主机都能访问

# if __name__ == '__main__':
#     nowtime = time.time()
#     startexam('87a2EDGxCc9+aOnPPnCn6blWtAntkfu2OAnWQk93FpOJi7Q/370235', '安全、标准、材料、资料、监理员')
#     print(time.time() - nowtime)
