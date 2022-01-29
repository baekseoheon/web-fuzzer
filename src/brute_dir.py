#!/bin/python3

import os
import sys
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
    print("------------------------------")
    print("created wordlist queue")
    print("------------------------------\n")

    try:
        with open(wl_file) as fp:
            print("------------------------------")
            print("file open succeed")
            print("------------------------------\n")
        
            dict_names = fp.readline()
            print("------------------------------")
            print("a line was read from the file ")
            print("------------------------------\n")
            while dict_names:
                dict_name_word = dict_names.strip()
                words.put(dict_name_word)
                dict_names = fp.readline()
            print("------------------------------")
            print("created wordlist queue")
            print("------------------------------\n")

        fp.close()
        return words
    except:
        print("there is no file : %s" % wl_file)
        sys.exit(0)
    
def brute_dir(word_queue, target, extensions=None):

    while not word_queue.empty():
        
        if word_queue.empty():
            print("wordlist queue empty!")
            return -1;
            
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
                        print("found : [{}] ==> {}\n".format(res.status, url))
                    #else:
                     #   print(f'can\'t find : {url}\n')
                else:
                    print(f'there is no data : {url}\n')
            
            except(e.URLError, e.HTTPError):
                if hasattr(e.HTTPError, 'code') and e.HTTPError.code != 404:
                    print("!!! [{}] ==> {}".format(e.HTTPError.code, url))
                pass
            


if __name__ == "__main__":
    d_queue = create_wordlist(wl_file)
    target = input("target : ")
    print("brute_dir() starting...\n")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = [executor.submit(brute_dir, d_queue, target ,ext) for _ in range(10)]
        print("working...\n")
