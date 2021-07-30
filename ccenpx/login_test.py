import requests

url = 'https://api.ccenpx.com.cn/login/login'
headers = {
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
data = 'txt_username=510113198511100016&txt_password=0016&txt_type=1&txt_captcha=&txt_md5=0637d1e2d4e93b1c83cea6711488a162&txt_ic=300&txt_captcha_change=1'
print(requests.post(url=url, data=data, headers=headers).text)
