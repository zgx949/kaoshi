import re

from selenium import webdriver
import time
import requests
import urllib.parse

print("正在读取账号...")
f = open('C:\\Users\\Administrator\\Desktop\\' + input('请输入桌面上的文件名：'), 'r', encoding="utf-8")
idcards = f.read().splitlines()


def get_class(majorid_, userid_):
    majorid_ = urllib.parse.unquote(majorid_)
    userid_ = urllib.parse.unquote(userid_)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.ccenpx.com.cn',
        'Connection': 'keep-alive',
        'Referer': 'https://www.ccenpx.com.cn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Cache-Control': 'max-age=0',
    }

    data = {
        'txt_majorid': majorid_,
        'txt_userid': userid_
    }
    res = []
    response = requests.post('https://api.ccenpx.com.cn/Pcexamstudent/mystudy_major', headers=headers, data=data)
    if response:
        data_list = response.json()['data'][0]['data']
        for item in data_list:
            for i in item['children']:
                res.append({'url': i['url'], 'id': i['id']})

    return res


def post_data(userid_, auth, vid, majorid_, currtime, durtion):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
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

    params = (
        ('uid', userid_),
    )

    data = {
        'auth': auth,
        'txt_userid': userid_,
        'txt_videoid': vid,
        'txt_action': 'end',
        'txt_currtime': currtime,
        'txt_errorinfo': '',
        'txt_majorid': majorid_,
        'duration': durtion
    }

    response = requests.post('https://api.ccenpx.com.cn/Pcexamstudent/videoAction', headers=headers, params=params,
                             data=data)
    print(response.text)


if __name__ == "__main__":
    driver = webdriver.Firefox()
    for idcard in idcards:
        driver.delete_all_cookies()
        driver.get('https://www.ccenpx.com.cn/platform/login/p/type/1')
        try:
            driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[1]/div[2]/input').send_keys(idcard)
            driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[2]/div[2]/input').send_keys(idcard[-4:])
        except:
            print('自动填入账号错误，请手动复制登录：', idcard)
        try:
            driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()
        except:
            pass
        time.sleep(2)

        while driver.current_url == 'https://www.ccenpx.com.cn/platform/login/p/type/1':
            time.sleep(1)
        driver.get('https://www.ccenpx.com.cn/student/mystudy/major/p/menu/mystudy_major')

        while 'https://www.ccenpx.com.cn/student/mystudy/p/menu/mystudy?major_id=' not in driver.current_url:
            time.sleep(1)

        input("回车键开始 ")

        majorid = driver.execute_script('return major_id;')
        userid = driver.execute_script('return user_id;')
        data = get_class(majorid, userid)
        html = driver.page_source
        auth = re.findall(r"auth = '(.*?)';", html)[0]

        for i in data:
            time.sleep(2)
            driver.execute_script('videoId = ' + str(i['id']) + ';')
            driver.execute_script('play({})'.format(i['url']))

            try:
                driver.find_element_by_xpath(
                    '/html/body/div/div[1]/div[2]/div[3]/div/div/div[2]/div/div/div/div/button/span[1]').click()
                time.sleep(1)
            except:
                print('播放失败')
            try:
                driver.execute_script(
                    'document.getElementsByTagName("video")[0].currentTime=document.getElementsByTagName("video")[0].duration-3')
            except Exception as e:
                print(e)
            try:
                durtion = driver.execute_script('return document.getElementsByTagName("video")[0].duration')
                post_data(userid, auth, str(i['id']), majorid, durtion, durtion)

            except Exception as e:
                print(e)

            print('已完成：', i)

        input('按回车键进入下一个')
        try:
            driver.execute_script('loginOut()')
        except:
            try:
                driver.find_element_by_xpath('/html/body/div/div[1]/div[1]/div/div[2]/div[5]/a/div').click()
            except:
                print('请手动退出账号')
        time.sleep(1)
