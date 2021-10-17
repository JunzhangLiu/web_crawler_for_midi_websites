import requests, pickle
from bs4 import BeautifulSoup
import json
import os
import requests

from os.path import dirname
from os.path import exists

# cookies = {
#     'menunew': '6-6-6-6',
#     'PHPSESSID': '',
#     'think_language': 'zh-CN',
#     'huiyuan': '',
#     'FWE_getuser': '',
#     'FWE_getuserid': '',
#     'login_mima': '',
# }



# response = requests.get('https://www.everyonepiano.cn/Music-class12-%5E%%5EE5%5E%%5E8A%5E%%5EA8%5E%%5EE6%5E%%5EBC%5E%%5EAB.html', headers=headers, cookies=cookies)

class Midi_crawler(object):
    def __init__(self,urls,b,load_cookie=False):    
        self.s = requests.Session() 
        self.s.headers = {
                                'Connection': 'keep-alive',
                                'Cache-Control': 'max-age=0',
                                'sec-ch-ua': '^\\^',
                                'sec-ch-ua-mobile': '?0',
                                'Upgrade-Insecure-Requests': '1',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                                'Sec-Fetch-Site': 'same-origin',
                                'Sec-Fetch-Mode': 'navigate',
                                'Sec-Fetch-User': '?1',
                                'Sec-Fetch-Dest': 'document',
                                'Referer': 'https://www.everyonepiano.cn/Music.html',
                                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
                            }
        self.urls = urls
        self.b = b
        self.success = []
        self.fail = []

        self.s.cookies.update({
                                'menunew': '6-6-6-6',
                                'PHPSESSID': '', #fill in
                                'think_language': 'zh-CN',
                                'huiyuan': '', #fill in
                                'FWE_getuser': '', #fill in
                                'FWE_getuserid': '', #fill in
                                'login_mima': '', #fill in
                            })

    # def login(self):
    #     front_page,success = self.send_request(self.b)
    #     if not success:
    #         exit()
    #     login_link = front_page.find("a",title="登录")["href"]
    #     login_page, success = self.send_request(self.b)
    #     if not success:
    #         exit()
    def send_request(self,url):
        try:
            return self.s.get(url).text, True
        except Exception as e:
            return e, False
    
    def send_midi_request(self,url):
        try:
            return self.s.get(url), True
        except Exception as e:
            return e, False

    def load_list(self):
        page, success = self.send_request(url)
        if not success:
            print("failed to receive respond, exit", page)
            return
        soup = BeautifulSoup(page, 'lxml')
        self.enumerate_links(soup)
            
    def enumerate_links(self,soup):
        # links = soup.find_all("a",class_="Title")
        midi_list = []
        page_list = soup.find("div",class_="col-xs-8 col-sm-8 col-md-7 pagelist")
        next_page_link = page_list.find_all("a")[-1]
        reached_last_page = False
        num_success, num_fail = 0,0
        i = 1
        while not reached_last_page:
            print("page",i)
            next_page_link = page_list.find_all("a")[-1]
            if next_page_link.contents[0] != " > ":
                reached_last_page = True
            i+=1
            
            try:
                music_list = soup.find_all("a",class_ = "Title")[1:]
            except Exception as e:
                continue

            for a in music_list:
                midi_list.append(self.b+a["href"])

            for j in range(10):
                next_page, success = self.send_request(self.b+next_page_link["href"])
                soup = None
                page_list = None
                if success:
                    soup = BeautifulSoup(next_page, 'lxml')
                    page_list = soup.find("div",class_="col-xs-8 col-sm-8 col-md-7 pagelist")
                    if page_list is not None:
                        break
            if soup is None or page_list is None:
                exit()
                
        num = 0
        for music_link in midi_list:
            if exists('./midis3/'+str(num)+".mid"):
                num+=1
                continue
            music_page, success = self.send_request(music_link)
            if not success:
                print("failed to open music page",num)
                for i in range(10):
                    print("try",i)
                    music_page, success = self.send_request(music_link)
                    if success:
                        break
                if not success:
                    print("failed to open music page",num)
                    num+=1
                    num_fail+=1
                    continue
            soup = BeautifulSoup(music_page, 'lxml')
            midi_link = soup.find_all("a",title="Midi文件下载")
            if len(midi_link)==0:
                continue
            midi_link = self.b+midi_link[0]["href"]
            
            midi_page, success = self.send_request(midi_link)
            if not success:
                print("failed to open page", num)
                for i in range(10):
                    print("try", i)
                    midi_page, success = self.send_request(midi_link)
                    if success:
                        break
                if not success:
                    print("failed to open midi page", num)
                    num+=1
                    num_fail+=1
                    continue
            soup = BeautifulSoup(midi_page, 'lxml')
            midi_button = soup.find("a",class_="btn btn-success btn-block BtnDown")
            
            mid,success = self.send_midi_request(self.b+midi_button["href"])
            if not success:
                print("Faild to download midi", num)
                for i in range(10):
                    print("try",i)
                    mid,success = self.send_midi_request(self.b+midi_button["href"])
                    if success:
                        break
                if not success:
                    print("failed to download midi",num)
                    num+=1
                    num_fail+=1
                    continue
            if "<!doctype html>" in str(mid.text):
                print("f")
            
            with open('./midis3/'+str(num)+".mid", 'wb') as midi_file:
                print('saving midi',num)
                midi_file.write(mid.content)
            num_success+=1
            num+=1
        print("total download attempt",num)
        print("success",num_success)
        print("fail",num_fail)
        
b = "https://www.everyonepiano.cn"
url = "https://www.everyonepiano.cn/Music-class12-%E5%8A%A8%E6%BC%AB.html"
crawler = Midi_crawler(url,b)
crawler.load_list()