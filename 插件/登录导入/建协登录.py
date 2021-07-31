from selenium import webdriver
import time
import requests
import os
import requests
from hashlib import md5
import base64
import json


class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password = password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


def main(path, fname, driver):
    idcards = []
    with open(path + '\\' + fname, encoding='utf-8', mode='r') as f:
        idcards = f.read().splitlines()

    for idcard in idcards:
        if len(idcard) < 18:
            continue
        driver.get('https://www.ccenpx.com.cn/platform/login/p/type/1')
        driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[1]/div[2]/input').send_keys(idcard)
        driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[2]/div[2]/input').send_keys(idcard[-4:])
        # driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[3]/div[2]/div[2]/span').click()

        # while True:
        #     try:
        #         imgelement = driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[3]/div[2]/div[2]/img')    # 定位验证码
        #         break
        #     except:
        #         time.sleep(1)
        #         continue

        # img_base64 = imgelement.get_attribute("src").split(',')[1]      # 验证码的base64
        # img_ocr_data = Chaojiying_Client('zgx949', 'zgx949', '919971').PostPic(base64.b64decode(img_base64), 2004)  # 识别验证码返回的信息

        # driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[3]/div[2]/input').send_keys(img_ocr_data['pic_str'])   # 输入验证码
        try:
            driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()  # 登录
        except:
            pass

        while driver.current_url != 'https://www.ccenpx.com.cn/student/home':
            time.sleep(1)

        userid = str(driver.execute_script('return localStorage.getItem("userId")'))
        img = str(driver.execute_script('return localStorage.getItem("avatUrl")'))
        name = str(driver.execute_script('return localStorage.getItem("realName")'))

        print(fname.replace('.txt', '') + '\n', idcard + '\n', userid + '\n', img + '\n', name + '\n')
        respon = requests.post(
            url='http://localhost:8000/adduser',
            data=json.dumps({"classname": fname.replace('.txt', ''), "id_card": idcard, "name": name, "icon_url": img,
                             "userid": userid}),
            headers={
                'Content-Type': 'application/json',
            }
        )
        print(respon.json())
        try:
            driver.execute_async_script("loginOut();")
            break
        except Exception as e:
            print(e)


if __name__ == '__main__':
    path = r'D:\codes\py\django\建协系统\user'
    driver = webdriver.Firefox()
    input("配置完代理按回车键开始")
    for name in os.listdir(path):
        main(path, name, driver)

    # im = open(r'C:\Users\Administrator\Desktop\1.txt', encoding='utf-8', mode='r').read().split(',')[1]
    # print(Chaojiying_Client('zgx949', 'zgx949', '919971').PostPic(base64.b64decode(im), 2004))
