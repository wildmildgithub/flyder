from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser

from multiprocessing.queues import Empty
from multiprocessing import Pool, Process, Queue, Value, cpu_count

import tqdm
import time
import requests
import re

class FlyderParser:

    
    def __init__(self, chunk):
        self.LINK_REGEX     = re.compile('((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', re.DOTALL)
        self.EMAIL_REGEX    = re.compile('[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
        self.HEADERS        = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
        self.api_endpoint   = "https://flyder.io/nodeapi/api/email/insert"
        self.chunk          = chunk
        self.urls           = []

    def parse(self, url):
        response = requests.get(url)
        emails   = re.findall( self.EMAIL_REGEX, response.text )

        if emails:
            for email in email:
                all_data.append({ source: url, email: email })

    def spread(self):
        urls_list = re.findall( self.LINK_REGEX , self.chunk.decode())
        for url in urls_list:
            self.urls.append( url[0] )

        with Pool(processes=cpu_count() * 2 ) as pool, tqdm.tqdm(total=len(self.urls)) as pbar:
            all_data = []
            for data in pool.imap_unordered(self.parse, self.urls):
                all_data.extend(data)
                pbar.update()

            requests.post( self.api_endpoint, data=all_data )
