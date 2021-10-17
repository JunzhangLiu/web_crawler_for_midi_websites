import requests, pickle
from bs4 import BeautifulSoup
import json
import os

class Midi_crawler(object):
    def __init__(self,urls=[],load_cookie=False):    
        self.s = requests.Session() 
        self.s.headers = {'User-Agent': 'Mozilla/5.0'}
        self.urls = urls
        
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
        links = soup.find_all("tr")
        num_midi_saved = 0
        for i in links:
            for j in i.find_all("a"):
                try:
                    l = j["href"]
                    if ".mid" in l:
                        mid = self.s.get(self.urls+l)
                        with open('./midis2/'+l, 'wb') as midi_file:
                            print('saving midi',l)
                            midi_file.write(mid.content)
                        num_midi_saved+=1
                except Exception as e:
                    print(e)
        print(num_midi_saved)
    def summary(self):
        summary_file = open('summery.txt','w')
        print('success:',file=summary_file)
        for i in self.success:
            print(i,file=summary_file)
        print('fail:', file=summary_file)
        for i in self.fail:
            print(i,file=summary_file)
        summary_file.close()

url = "http://www.vgmusic.com/music/console/sega/master/"
crawler = Midi_crawler(url)
crawler.load_list()