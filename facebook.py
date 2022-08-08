#-*- coding:utf-8 -*-
from selenium import webdriver
# from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from proxy_utils import get_Proxy
from header_utils import add_Header
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
from random import randint,uniform
from lxml import etree
import pickle
import os
import pandas as pd

class Facebook(object):
    def __init__(self,proxy_ip,proxy_port,proxy_username,proxy_password,username,password):

        self.proxy_ip=proxy_ip
        self.proxy_port=proxy_port
        self.proxy_username=proxy_username
        self.proxy_password=proxy_password
        self.username=username
        self.password=password
        self.proxy=get_Proxy(self.proxy_ip,self.proxy_port,self.proxy_username,self.proxy_password)
        self.option = webdriver.ChromeOptions()

        # self.option.add_argument("--headless")
        # self.option.add_argument("--disable-gpu")

        if self.proxy is not None:
            self.option.add_argument(self.proxy)

        self.headers = {
            "origin": "https://www.facebook.com",
            "referer": "https://www.facebook.com",
            "sec-ch-prefers-color-scheme": "light",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-Agent": " Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v = "104", " Not A;Brand";v = "99", "Google Chrome";v = "104"'
        }

        self.option=add_Header(self.option,self.headers)

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.option)

        self.main()

    #启动登陆facebook的功能选择：包括密码登陆和cookies两种方式
    def login_facebook(self):
        if os.path.exists("./facebook_cookies.pkl") == False:
             self.login_facebook_with_username_password()
        else:
            self.login_with_cookies()

        self.driver.refresh()
        sleep(5)
        print("登陆完毕！")

    #使用cookies登陆
    def login_with_cookies(self):
        login_url = "https://www.facebook.com/"
        self.driver.get(login_url)
        cookies=pickle.load(open("./facebook_cookies.pkl","rb"))
        for cookie in cookies:
            if isinstance(cookie.get('expiry'), float):
                cookie['expiry'] = int(cookie['expiry'])

            self.driver.add_cookie(cookie)

    #使用账户密码登陆
    def login_facebook_with_username_password(self):
        try:
            login_url="https://www.facebook.com/"
            check_url="https://www.facebook.com/checkpoint/?next"
            self.driver.get(login_url)
            # 切换输入用户名和密码的界面
            WebDriverWait(self.driver, 10, 0.5).until(EC.element_to_be_clickable((By.NAME, "login")))

            #输入用户名
            WebDriverWait(self.driver, 2, 0.5).until(EC.presence_of_element_located((By.NAME, "email")))
            self.driver.find_element_by_id("email").send_keys(self.username)

            #输入密码
            WebDriverWait(self.driver, 2, 0.5).until(EC.presence_of_element_located((By.ID, "pass")))
            self.driver.find_element_by_id("pass").send_keys(self.password)

            #点击确定
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()

            # 检测是否需要验证码
            sleep(5)

            while True:
                cur_url = self.driver.current_url
                if cur_url == check_url:
                    sleep(3)
                else:
                    break

            print("登陆成功啦")

            cookies=self.driver.get_cookies()
            pickle.dump(cookies, open('facebook_cookies.pkl', 'wb'))
        except Exception as e:
            print(e)

    #检查页面内容是否加载完成
    def check_end(self):
        try:
            element=self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[last()]').text

            if element=="已经到底啦~":
                return True
            else:
                return False
            # 原文是except NoSuchElementException, e:
        except NoSuchElementException as e:
            # 发生了NoSuchElementException异常，说明页面中未找到该元素，返回False
            return False



    #获取更新页面内容
    def get_info(self):
        download_url=input("需要爬去的页面为:")
        self.driver.refresh()
        sleep(uniform(5, 10))
        self.driver.get(download_url)
        temp_height = 0
        while True:
            sleep(uniform(5, 10))
            #页面滚动，每次都在上次的基础上继续延伸
            self.driver.execute_script("window.scrollTo(0,"+str(temp_height+randint(200,8000))+");")
            self.driver.implicitly_wait(10)
            sleep(uniform(5,10))
            # # 获取当前滚动条距离顶部的距离
            check_height = self.driver.execute_script(
                "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")
            if self.check_end():
                print("页面内容全部加载完毕")
                self.deal_info()
                break
            else:
                temp_height=check_height
                print(temp_height)


    #对获取好的内容进行处理和保存
    def deal_info(self):
        save_file = input("需要保存的文件名为:")
        userids,publish_time,infos=[],[],[]
        html=self.driver.page_source
        content=etree.HTML(html)
        tables=content.xpath("//div[@class='d2edcug0 o7dlgrpb']/div")
        for i in range(0,len(tables)-1):
            tmp_userids = tables[i].xpath(
                "div/div/div/div/div/div/div/div/div/div/div[8]/div/div[2]/div/div[2]/div/div[1]/span/h3//text()")
            userid = ""
            for tmp_userid in tmp_userids:
                if tmp_userid not in ['\xa0']:
                    userid += str(tmp_userid)

            true_time=None
            tmp_times = tables[i].xpath(
                "div/div/div/div/div/div/div/div/div/div/div[8]/div/div[2]/div/div[2]/div/div[2]/span/span//text()")
            for tmp_time in tmp_times:
                if tmp_time not in ['\xa0', ' · ', '=']:
                    true_time = tmp_time
                    break

            items = tables[i].xpath(
                "div/div/div/div/div/div/div/div/div/div/div[8]/div/div[3]/div[1]/div/div/div/span//text()")
            item_str = ""
            for item in items:
                item_str += item


            userids.append(userid)
            publish_time.append(true_time)
            infos.append(item_str)

        df=pd.DataFrame()
        df["用户"]=userids
        df["发布时间"]=publish_time
        df["内容"]=infos
        df.to_excel("./res/"+str(save_file)+".xlsx",encoding="utf-8")



    def main(self):

        try:
            #登陆到facebook
            self.login_facebook()

            #输入需要爬虫的网址
            while True:
                download_flag= input("是否需要爬取内容(y:表示爬取,n:表示结束):")
                if download_flag == "y":
                    self.get_info()
                elif download_flag == "n":
                    print("facabook停止爬取！")
                    exit()
                else:
                    print("输入有误，请重新输入")

        except Exception as e:
            print(e)
        finally:
            exit()







if __name__ == '__main__':
    username="xxxxxx"
    password="xxxxxx"
    proxy_ip="127.0.0.1"
    proxy_port="8080"
    proxy_username=None
    proxy_password=None
    a=Facebook(proxy_ip,proxy_port,proxy_username,proxy_password,username,password)

