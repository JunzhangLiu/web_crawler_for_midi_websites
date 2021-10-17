import requests, pickle
from bs4 import BeautifulSoup
import json
import os

class Midi_crawler(object):
    def __init__(self,urls,url_dir):    
        self.s = requests.Session() 
        self.s.headers = {'User-Agent': 'Mozilla/5.0'}
        self.urls = urls
        self.url_dir = url_dir
        
        self.success = []
        self.fail = []
        
    def add_log(self,success,url,message,e):
        if success:
            self.success.append((url, message,e))
        else:
            self.fail.append((url, message,e))

    def send_request(self,url):
        try:
            return self.s.get(url).text, True
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
        sys = soup.find_all("p",{"class": "sys"})
        num_midi_saved=0
        for i in sys:
            print(i)
            sys_link = i.find_all("a")[0]["href"]
            sys_page, success = self.send_request(self.url_dir+sys_link)
            if not success:
                continue
            sys_soup = BeautifulSoup(sys_page, 'lxml')
            musics = sys_soup.find_all("p", {"class": "choose"})
            for j in musics:
                download_link=j.find_all("a")[0]["href"]
                download_page, success = self.send_request(self.url_dir+sys_link[:-10]+download_link)
                if not success:
                    continue
                download_soup = BeautifulSoup(download_page, 'lxml')
                for k in download_soup.find_all("p", {"class": "ju"}):
                    try:
                        mid_name = k.find_all("a")[0]["href"]
                        if ".mid" in mid_name:
                            mid_link = self.url_dir+sys_link[:-10]+download_link[:-10]+mid_name
                            mid = self.s.get(mid_link)
                            with open('./gt_midis/'+mid_name, 'wb') as midi_file:
                                print(num_midi_saved,'saving midi',mid_name)
                                midi_file.write(mid.content)
                            num_midi_saved+=1
                            break
                    except Exception as e:
                        continue
    def summary(self):
        summary_file = open('summery.txt','w')
        print('success:',file=summary_file)
        for i in self.success:
            print(i,file=summary_file)
        print('fail:', file=summary_file)
        for i in self.fail:
            print(i,file=summary_file)
        summary_file.close()

url = "http://www.gamemusicthemes.com/sheetmusic/index.html"
url_dir = "http://www.gamemusicthemes.com/sheetmusic/"
crawler = Midi_crawler(url,url_dir)
crawler.load_list()