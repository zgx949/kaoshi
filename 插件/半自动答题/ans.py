from selenium import webdriver
import re
import json
import os
import time
import requests
import os
from fuzzywuzzy import fuzz
from urllib import parse


# print("正在读取题库...")
# f = open(r'C:\Users\Administrator\Desktop\1.txt','r',encoding="utf-8")
# text=f.read()
# likesp = int(input("请输入相似度:"))
#questions=re.findall('题：(.*?)。',text)
#questions=re.findall('\n(.*?)。',text)
# questions=re.findall(r'题：(.*?)\n',text)
#answers=re.findall(r'答案(.*?)\n',text)
# answers=re.findall(r'答案：(.*?)\n',text)
# dbug=input("任意键继续")
# print('题目共：'+str(len(questions))+"\n答案共："+str(len(answers)))
# if(len(questions)==len(answers)):
#     print("题库答案匹配成功!")
# else:
#     print("题库答案匹配有误")
#处理多选题答案
#print(answers)
# for i in range(len(answers)):
#     if(len(answers[i])>1):
#         str_new=''
#         for n in range(len(answers[i])):
#             if(n!=len(answers[i])):
#                 str_new=str_new+answers[i][n]+','
#         answers[i]=str_new[0:-1]    

#print(answers)
#print(questions)
# for t in range(len(answers)):
#     print(answers[t]+questions[t])
# for que in questions:
#     print(que)
print("正在读取账号...")
f = open(r'C:\Users\Administrator\Desktop\2.txt','r',encoding="utf-8")
idcards = f.read().splitlines()
print('读取成功！\n正在初始化图片识别模块...')
access_token = requests.get(url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=4y4KEQbtIz7IG7D7gIGw9sVW&client_secret=aupCv8FLh81blzNa1CLwQk71z14MBNuF').json()['access_token']

def OCR(base64):
    if(len(base64) <= 1000):
        return base64
    global access_token
    base64 = base64[5:-3]
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    params = {"image":base64}
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




def answer_save(userid,majorid,placeid,paperid,dataid,topicid,answer):
    """
    提交答案
    """
    url=r'https://api.ccenpx.com.cn/official/official_save'
    data={'txt_userid':userid,
'txt_majorid':majorid,
'txt_placeid':placeid,
'txt_paperid':paperid,
'txt_dataid':dataid,
'txt_topicid':topicid,
'txt_answers':answer,
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
    html=requests.post(url=url,data=data, headers=headers).text
    json_data=json.loads(html)
    print(dataid+'提交成功：'+answer)
def get_answer(userid,majorid,placeid,paperid,dataid):
    '''
    获取题目列表
    '''
    url=r'https://api.ccenpx.com.cn/official/official_topic'
    data={'txt_userid':userid,
    'txt_majorid':majorid,
    'txt_placeid':placeid,
    'txt_paperid':paperid,
    'txt_type':'1',
    'txt_dataid':dataid,
    }
    headers={
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
    rehtml=requests.post(url=url,data=data,headers=headers).text
    if '请稍后再试' in rehtml:
        rehtml = get_answer(userid,majorid,placeid,paperid,dataid)
        return rehtml
    import json
    # print(rehtml)
    html = json.loads(rehtml)
    try:
        dataid = html['data']['data_id']
    except TypeError:
        print(str(html) + '\n正在重新请求...')
        return get_answer(userid,majorid,placeid,paperid,dataid)
    # str_data=re.findall('data_id\":\"(.*?)\",',html)[0]
    # dataid=str_data.replace('\\','')
    # str_data=re.findall('topic_id\":\"(.*?)\",',html)[0]
    # topicid=str_data.replace('\\','')
    topicid = html['data']['topic_id']
    content = html['data']['content'].replace('src=\"','')[0:-1]
    questions_text = OCR(content)
    print(questions_text)
    ##寻找答案，没有答案则选A

    answers = requests.get('http://127.0.0.1:8000/ans', params={'classname':'安全员', 'likes': '90', 'question': questions_text.replace(' ', '')}).json()['options']
    if answers == None:
        return rehtml
    print('正在提交答案')
    answer_save(userid,majorid,placeid,paperid,dataid,topicid,answers)

    # for i in range(len(questions)):
    #     likes=fuzz.ratio(questions[i], questions_text)
    #     if(likes>int(likesp)):
    #         answer_save(userid,majorid,placeid,paperid,dataid,topicid,answers[i])
    #         print('正在提交答案...相似度：'+str(likes))
    #         break
    #     else:
    #         if(i==len(questions)-1):
    #             print('没找到答案，已放空！')

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
        'file_base64':img_base64,
    }
    headers = {
        'Connection': 'Keep-Alive',
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
    }
    
    json_data = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params,  headers=headers).json()
    return json_data['pic_str']





    

if __name__ == "__main__":
    
    
    # while(True):
    for idcard in idcards:
        # input('按回车启动浏览器')
        driver=webdriver.Firefox()
        driver.get('https://www.ccenpx.com.cn/platform/login/p/type/1')

        driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[1]/div[2]/input').send_keys(idcard)
        driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[2]/div[2]/input').send_keys(idcard[-4:])
        try:
            driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[3]/div[2]/div[2]/span').click()
        except:
            pass
        time.sleep(2)

        # img_yzm_base64 = driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[3]/div[2]/div[2]/img').screenshot_as_base64
        
        

        # driver.execute_script("$('.captchaApi').html('<input type=\"hidden\" name=\"captcha_md5\" value=\"'+'05e59dfb91a40c97198c6b0e1d53caac'+'\">')")
        # yzm = '响夜却覆'
        # driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[3]/div[2]/input').send_keys(yzm)
        # driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()
        # driver.get('https://www.ccenpx.com.cn/testcenter/testcenter_official.php?menu=official')
        # time.sleep(1)
        while driver.current_url == 'https://www.ccenpx.com.cn/platform/login/p/type/1':
            time.sleep(1)

        # try:
        #     driver.find_element_by_xpath('/html/body/div/div[1]/div[1]/div/div[2]/div[2]/a/div').click()
        # except:
        #     print('请手动打开考试页面')
        driver.get('https://www.ccenpx.com.cn/student/official/p/menu/official')
        driver.get('https://www.ccenpx.com.cn/testcenter/testcenter_official.php?menu=official')
        try:
            driver.find_element_by_xpath('/html/body/div/div[1]/div[2]/div[3]/div[1]/div[2]/div/a/span').click()
        except:
            input('请手动打开考试页面')
        # if(input('请先打开考试承诺页面，任意键开始答题(输入：0代表关闭程序)')=='0'):
        #     exit()
        input("回车键开始 ")
        try:
            userid=driver.execute_script('return localStorage.getItem("userId")')
            majorid=driver.execute_script('return localStorage.getItem("majorId")')
            placeid=driver.execute_script('return localStorage.getItem("placeId")')
            paperid=driver.execute_script('return localStorage.getItem("paperId")')
            # try:
            print('userid:\n'+userid+'\n'+'majorid：\n'+majorid+'placeid:\n'+placeid+'paperid:\n'+paperid)
            if(majorid==''):
                print('请先打开考试承诺页面！')
                #driver.close()
                continue

        except:
            print('请先打开考试承诺页面！')
            #driver.close()
            
            continue
        # driver.get('https://www.ccenpx.com.cn/testcenter/testcenter_official_topic.php')
        json_data=get_answer(userid,majorid,placeid,paperid,'0')
        # print(json_data)
        # id = json_data['data']['total']['topic']
        id=re.findall('\"id\":\"(.*?)\",',json_data)
        
        
        for i in range(6,55):
            str_data=id[i]
            dataid=str_data.replace('\\','')
            # dataid = id
            get_answer(userid,majorid,placeid,paperid,dataid)
        print('完成')
        if(input('是否继续？（输入0退出，任意键交卷并继续）')=='0'):
            try:
                driver.execute_script('finish();')
                driver.find_element_by_css_selector('.layui-layer-btn0').click()
            except:
                pass
            driver.close()
            exit()
        else:
            continue
            driver.close()
            # time.sleep(2)
