from selenium import webdriver
import re
import json
import time
import requests

print("正在读取账号...")
f = open('C:\\Users\\Administrator\\Desktop\\' + input('请输入桌面上的文件名：'), 'r', encoding="utf-8")
idcards = f.read().splitlines()
print('读取成功！\n正在初始化图片识别模块...')

if __name__ == "__main__":
    driver = webdriver.Firefox()
    for idcard in idcards:
        # input('按回车启动浏览器')

        driver.get('https://www.ccenpx.com.cn/platform/login/p/type/1')

        driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[1]/div[2]/input').send_keys(idcard)
        driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[2]/div[2]/input').send_keys(idcard[-4:])
        try:
            driver.find_element_by_xpath('/html/body/div[4]/div[1]/form/div/div[3]/div[2]/div[2]/span').click()
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
                classname = '通用'

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


        except:
            print('请先打开考试承诺页面！')
            driver.get('https://www.ccenpx.com.cn/student/home')
            try:
                driver.execute_async_script("loginOut();")
                break
            except Exception as e:
                print(e)

            continue
        for i in range(50):
            try:
                time.sleep(1)
                quesion = driver.find_element_by_xpath('//*[@id="content"]').text  # 获取题目内容
                answers = requests.get('http://127.0.0.1:8000/ans',
                                       params={'classname': classname, 'likes': '90',
                                               'question': quesion.replace(' ', '')}
                                       ).json()['options']
                if answers == None:
                    answers = ''
                answers = answers.replace('A', '1').replace('B', '2').replace('C', '3').replace('D', '4').replace('E',
                                                                                                                  '5')
                if answers != '':
                    for answer in answers:  # 选择答案
                        driver.find_element_by_xpath(
                            '/html/body/div[1]/div[2]/div[3]/div[2]/div[4]/div[{}]/input'.format(answer)).click()

                time.sleep(1)
                # 下一题
                driver.find_element_by_xpath('//*[@id="next"]').click()
            except Exception as e:
                print(e)
                continue
        time.sleep(2)
        try:
            driver.find_element_by_xpath('/html/body/div[4]/div[3]/a[1]').click()
        except:
            pass

        print('完成')
        if input('是否继续？（输入0退出，任意键交卷并继续）') == '0':
            try:
                driver.execute_script('finish();')
                driver.find_element_by_css_selector('.layui-layer-btn0').click()
            except:
                pass
            driver.get('https://www.ccenpx.com.cn/student/home')
            try:
                driver.execute_async_script("loginOut();")
                break
            except Exception as e:
                print(e)
            exit()
        else:
            continue
            driver.get('https://www.ccenpx.com.cn/student/home')
            try:
                driver.execute_async_script("loginOut();")
                break
            except Exception as e:
                print(e)
