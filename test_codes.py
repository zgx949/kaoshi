# import requests
#
# proxies = {
#   "http": "http://103.44.245.120:16991",
#   "https": "http://103.44.245.120:16991",
# }
# r = requests.get('https://www.y-jiema.com/ip', proxies=proxies,verify=False,)
# print(r.text)


# coding=utf-8
import requests

# 请求地址
targetUrl = "https://www.y-jiema.com/ip"

# 代理服务器
proxyHost = "113.206.193.153"
proxyPort = "14030"

proxyMeta = "http://%(host)s:%(port)s" % {

    "host": proxyHost,
    "port": proxyPort,
}

proxies = {

    "http": proxyMeta,
    "https": proxyMeta
}

resp = requests.get(targetUrl, proxies=proxies)
print(resp.text)
