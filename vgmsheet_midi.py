import requests, pickle
from bs4 import BeautifulSoup
import json
import os

import requests
import zipfile
import warnings
from sys import stdout
from os import makedirs
from os.path import dirname
from os.path import exists


class GoogleDriveDownloader:
    """
    Minimal class to download shared files from Google Drive.
    """

    CHUNK_SIZE = 32768
    DOWNLOAD_URL = 'https://docs.google.com/uc?export=download'

    @staticmethod
    def download_file_from_google_drive(file_id, dest_path, overwrite=False, unzip=False, showsize=True):
        destination_directory = dirname(dest_path)
        status = True
        if not exists(destination_directory):
            makedirs(destination_directory)

        if not exists(dest_path) or overwrite:

            session = requests.Session()
            session.headers = {'User-Agent': 'Mozilla/5.0'}

            print('Downloading {} into {}... '.format(file_id, dest_path), end='')
            stdout.flush()

            response = session.get(GoogleDriveDownloader.DOWNLOAD_URL, params={'id': file_id}, stream=True)

            token = GoogleDriveDownloader._get_confirm_token(response)
            if token:
                params = {'id': file_id, 'confirm': token}
                response = session.get(GoogleDriveDownloader.DOWNLOAD_URL, params=params, stream=True)

            if showsize:
                print()  # Skip to the next line

            current_download_size = [0]
            status = GoogleDriveDownloader._save_response_content(response, dest_path, showsize, current_download_size)
            print('Done.')
        return status
    @staticmethod
    def _get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    @staticmethod
    def _save_response_content(response, destination, showsize, current_size):
        if "<html><head>" in str(response.content):
            return False
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(GoogleDriveDownloader.CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    if showsize:
                        current_size[0] += GoogleDriveDownloader.CHUNK_SIZE
                    
        print(GoogleDriveDownloader.sizeof_fmt(current_size[0]), end=' ')
        stdout.flush()
        return True

    # From https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    @staticmethod
    def sizeof_fmt(num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return '{:.1f} {}{}'.format(num, unit, suffix)
            num /= 1024.0
        return '{:.1f} {}{}'.format(num, 'Yi', suffix)






class Midi_crawler(object):
    def __init__(self,urls=[],load_cookie=False):    
        self.s = requests.Session() 
        self.s.headers = {'User-Agent': 'Mozilla/5.0'}
        self.urls = urls
        self.d = GoogleDriveDownloader()
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
        illegal_char = "\/:*?\"<>|~#%&+{\}-."
        tables = soup.find_all("table")
        num_midi_saved = len([name for name in os.listdir("./vgmsheet_midi/")])
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                try:
                    cells = row.find_all("td")
                    title = cells[0].contents[0]
                    for char in illegal_char:
                        if char in title:
                            title=title.replace(char,'')
                    link = cells[1].find_all("a")[1]["href"]
                    start = link.index("id=")+3
                    try:
                        status = self.d.download_file_from_google_drive(link[start:],"./vgmsheet_midi/"+title+".mid")
                        if not status:
                            print(num_midi_saved)
                            exit()
                        num_midi_saved+=1
                    except Exception as e:
                        print(e, "retry")
                        for i in range(5):
                            print("attempt",i)
                            try:
                                status = self.d.download_file_from_google_drive(link[start:],"./vgmsheet_midi/"+title+".mid")
                                if not status:
                                    print(num_midi_saved)
                                    exit()
                                num_midi_saved+=1
                                break
                            except Exception as e:
                                print(e,"failed")

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

url = "https://vgmsheetmusicbyolimar12345.com/piano-arrangements/"
gen_url = "https://sites.google.com/site/gdocs2direct/home"
crawler = Midi_crawler(url)
crawler.load_list()