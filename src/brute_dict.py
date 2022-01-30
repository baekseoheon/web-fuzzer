#!/bin/python3

import os
import queue
import time
import urllib3
import concurrent.futures
import urllib.parse as p 
import urllib.error as e

target = ''
# wordlist_file
wl_file = 'wordlist.txt'
ext = [".php", ".txt"]
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.77 Safari/537.36'

def create_wordlist(wl_file):
    is_resume = False
    words = queue.Queue()

    with open(wl_file) as fp:
        #if not os.path.isfile(fp):
            #break
        dict_names = fp.readline()
        while dict_names:
            dict_name_word = dict_names.strip()
            words.put(dict_name_word)
            dict_names = fp.readline()

    fp.close()
    return words
    
def brute_dir(word_queue, extensions=None):

    while not word_queue.empty():
        try_this = word_queue.get()
        try_list = []
        
        if '.' not in try_this:
            try_list.append("/{}/".format(try_this))
        else:
            try_list.append("/{}".format(try_this))
            
        if extensions:
            for extension in extensions:
                try_list.append("/{}{}".format(try_this, extension))
                
           # naver.com/blob
           # naver.com/.blob/
        for brute in try_list:
            url = "{}{}".format(target, p.quote(brute))
            try:
                http = urllib3.PoolManager()
                head = {}
                head["User_Agent"] = user_agent
                res = http.request("GET", headers=head, url=url)
                
                if len(res.data):
                    if res.status != 404:
                        print("[{}] ==> {}".format(res.status, url))
                    else:
                        print(f'can\'t find : {url}\n')
                else:
                    print(f'there is no data : {url}\n')
            
            except(e.URLError, e.HTTPError):
                if hasattr(e.HTTPError, 'code') and e.HTTPError.code != 404:
                    print("!!! [{}] ==> {}".format(e.HTTPError.code, url))
                pass
            
d_queue = create_wordlist(wl_file)

if __name__ == "__main__":
    target = input("target : ")
    print("brute_dir() starting...\n")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = [executor.submit(brute_dir, d_queue, ext) for _ in range(10)]
        print("working....\n")
