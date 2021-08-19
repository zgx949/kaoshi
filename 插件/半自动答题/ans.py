from fuzzywuzzy import fuzz
from selenium import webdriver
import re
import json
import time
import requests
import sqlite3

print("正在读取账号...")
f = open('C:\\Users\\Administrator\\Desktop\\' + input('请输入桌面上的文件名：'), 'r', encoding="utf-8")
idcards = f.read().splitlines()
print('读取成功！\n正在初始化图片识别模块...')
# access_token = requests.get(
#     url='https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=4y4KEQbtIz7IG7D7gIGw9sVW&client_secret=aupCv8FLh81blzNa1CLwQk71z14MBNuF').json()[
#     'access_token']

classname = ''
print("正在读取题库...")
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
sql = "select id, classname, question, option  from ccenpx_question_bank group by question"
cursor.execute(sql)
values = cursor.fetchall()
cursor.close()
conn.commit()
conn.close()
answers = {}
for qid, clname, qu, op in values:
    op = op.replace(',', '').replace(' ', '')
    temp = ''
    for i in op:
        temp += i + ','
    op = temp[:-1]
    answers[qu] = {'classname': clname, 'option': op}
print("题库共有：", len(values))

autofill = True
if input("未匹配答案是否处理？（按回车键自动填充A，输入其他任意则放空）"):
    autofill = False


def OCR(base64):
    if len(base64) <= 1000:
        return base64
    global access_token
    base64 = base64[5:-3]
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    params = {"image": base64}
    # access_token = '24.50a4b142def10530abe5f5b9ee3225d8.2592000.1621856548.282335-21795098'
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        text = ''
        for data in response.json()['words_result']:
            text += data['words']
        # print (text)
        return text


def answer_save(userid, majorid, placeid, paperid, dataid, topicid, answer):
    """
    提交答案
    """
    url = r'https://api.ccenpx.com.cn/official/official_save'
    data = {'txt_userid': userid,
            'txt_majorid': majorid,
            'txt_placeid': placeid,
            'txt_paperid': paperid,
            'txt_dataid': dataid,
            'txt_topicid': topicid,
            'txt_answers': answer,
            }
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
    html = requests.post(url=url, data=data, headers=headers).text
    json_data = json.loads(html)
    print(dataid + '提交成功：' + answer)


def get_answer(userid, majorid, placeid, paperid, dataid):
    '''
    获取题目列表
    '''
    url = r'https://api.ccenpx.com.cn/official/official_topic'
    data = {'txt_userid': userid,
            'txt_majorid': majorid,
            'txt_placeid': placeid,
            'txt_paperid': paperid,
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
    rehtml = requests.post(url=url, data=data, headers=headers).text
    if '请稍后再试' in rehtml:
        rehtml = get_answer(userid, majorid, placeid, paperid, dataid)
        return rehtml
    import json
    # print(rehtml)
    html = json.loads(rehtml)
    try:
        dataid = html['data']['data_id']
    except TypeError:
        print(str(html) + '\n正在重新请求...')
        return get_answer(userid, majorid, placeid, paperid, dataid)

    topicid = html['data']['topic_id']
    content = html['data']['content'].replace('src=\"', '')[0:-1]
    questions_text = OCR(content)
    print(questions_text)
    ##寻找答案，没有答案则选A

    # for i in range(len(questions)):
    for an in answers:

        likes = fuzz.ratio(an, questions_text)
        if likes >= 90 and classname[:1] in answers[an]['classname']:
            answer_save(userid, majorid, placeid, paperid, dataid, topicid, answers[an]['option'])
            print('正在提交答案...相似度：' + str(likes))
            return rehtml

    # answers = requests.get('http://127.0.0.1:8000/ans', params={'classname': classname, 'likes': '90',
    #                                                             'question': questions_text.replace(' ', '')}).json()[
    #     'options']
    if autofill:
        print('未匹配到答案，自动选A')
        answer_save(userid, majorid, placeid, paperid, dataid, topicid, 'A')
    else:
        print('放空')
    return rehtml


def ocr_yzm(img_base64):
    username = '18630052869'
    password = md5('ldd7368556'.encode('utf8')).hexdigest()
    soft_id = '917146'
    params = {
        'user': username,
        'pass2': password,
        'softid': soft_id,
        'codetype': 2004,
        'file_base64': img_base64,
    }
    headers = {
        'Connection': 'Keep-Alive',
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
    }

    json_data = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, headers=headers).json()
    return json_data['pic_str']


if __name__ == "__main__":
    driver = webdriver.Firefox()
    for idcard in idcards:
        # input('按回车启动浏览器')
        driver.delete_all_cookies()
        driver.get('https://www.ccenpx.com.cn/platform/login/p/type/1')

        driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[1]/div[2]/input').send_keys(idcard)
        driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[2]/div[2]/input').send_keys(idcard[-4:])
        try:
            driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()
        except:
            pass
        time.sleep(2)

        while driver.current_url == 'https://www.ccenpx.com.cn/platform/login/p/type/1':
            time.sleep(1)

        driver.get('https://www.ccenpx.com.cn/student/official/p/menu/official')
        # driver.get('https://www.ccenpx.com.cn/testcenter/testcenter_official.php?menu=official')
        try:
            driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div[1]/div[2]/div').click()
        except:
            input('请手动打开考试页面')

        input("回车键开始 ")
        try:
            userid = driver.execute_script('return localStorage.getItem("userId")')
            majorid = driver.execute_script('return localStorage.getItem("majorId")')
            placeid = driver.execute_script('return localStorage.getItem("placeId")')
            paperid = driver.execute_script('return localStorage.getItem("paperId")')
            name = driver.execute_script('return localStorage.getItem("realName")')
            img = driver.execute_script('return localStorage.getItem("avatUrl")')
            try:
                classname = driver.find_element_by_xpath('//*[@id="major"]').text
            except:
                classname = ''    # 通用

            print(
                classname + '\nuserid:\n' + userid + '\n' + 'majorid：\n' + majorid + 'placeid:\n' + placeid + 'paperid:\n' + paperid)
            if majorid == '':
                driver.get('https://www.ccenpx.com.cn/student/home')
                try:
                    driver.execute_async_script("loginOut();")
                    break
                except Exception as e:
                    print(e)
                continue
            # headers = {
            #     'Content-Type': 'application/json',
            # }
            # respon = requests.post(url='http://127.0.0.1:8000/adduser',
            #                        data=json.dumps({
            #                            'id_card': '0000',
            #                            'userid': userid,
            #                            'name': name,
            #                            'icon_url': img
            #                        }),
            #                        headers=headers
            #                        )  # 后台添加账号信息
            # if respon:
            #     print(respon.text)
            # respon = requests.post(url='http://127.0.0.1:5000/do',
            #                        data=json.dumps({
            #                            'majorid': majorid,
            #                            'placeid': placeid,
            #                            'paperid': paperid,
            #                            'userid': userid,
            #                            'classname': classname
            #                        }),
            #                        headers=headers
            #                        )  # 提交批量做题
            # if respon:
            #     print(respon.text)
            #
            # if majorid != '':
            #     input('回车键继续')
            #     driver.close()
            #     continue
            # else:
            #     input('账号出错！回车继续')
            #     driver.close()
            #     continue

        except:
            print('请先打开考试承诺页面！')
            driver.get('https://www.ccenpx.com.cn/student/home')
            try:
                driver.execute_async_script("loginOut();")
                break
            except Exception as e:
                print(e)

            continue
        json_data = get_answer(userid, majorid, placeid, paperid, '')
        id = re.findall('\"id\":\"(.*?)\",', json_data)

        for i in range(6, 55):
            str_data = id[i]
            dataid = str_data.replace('\\', '')
            get_answer(userid, majorid, placeid, paperid, dataid)
        print('完成')
        temp = input('是否继续？（输入0退出，任意键交卷并继续）')
        with open('已完成.txt', mode='a', encoding='utf-8') as f:
            if driver.current_url == 'https://www.ccenpx.com.cn/student/official/score':
                text = driver.find_element_by_xpath('/html/body/div/div[1]/div[3]/div[2]/div/div[3]').text
                if text == '考试合格':
                    f.write(idcard + '\t已通过\n')
                elif "补考" in text:
                    f.write(idcard + '\t不合格\n')
                else:
                    f.write(idcard + '\t未知\n')
            else:
                f.write(idcard + '\t未知\n')
        
        if temp != '0':
            try:

                driver.execute_script('finish();')
                driver.find_element_by_css_selector('/html/body/div[4]/div[3]/a[1]').click()

            except:
                pass
            time.sleep(1)
            driver.get('https://www.ccenpx.com.cn/student/home')
            try:
                driver.execute_async_script("loginOut();")
                break
            except Exception as e:
                print(e)

        else:
            exit()

