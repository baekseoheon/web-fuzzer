#!/bin/python3

import os
import re
import sys
import queue
import time
import urllib3
import requests
import concurrent.futures
import urllib.parse as p 
import urllib.error as e
import requests.exceptions as reqe

target = ''
# wordlist_file
wl_file = 'wordlist.txt'
ext = [".php", ".txt"]
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.77 Safari/537.36'

def delencode(url):
    url = url.replace("#", "")
    url = url.replace("%0A", "")
    url = url.replace("\n", "")
    url = url.replace("%40", "@")
    return url

def delschema(url):
    filename = url.replace("https://", "")
    filename = url.replace("http://", "")
    filename = re.sub("\/.*", "", filename)
    return filename

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

def dir_scan(target, wordlist, extensions=None):
    f = open(wordlist, "r")
    
    word = f.readline()
    while word != '':
        if word == '\n':
            word = f.readline()
            continue

        if word == '\0':
            word = f.readline()
            continue

        if '\n' in word:
           word = word.replace("\n", "")

        try_this = word
        try_list = []
        if extensions:
            if '.' not in try_this:
                if try_this == '/':
                    try_list.append("{}".format(try_this))
                else:
                    try_list.append("/{}/".format(try_this))
                    for extension in extensions:
                        try_list.append("/{}{}".format(try_this, extension))
            else:
                try_list.append("/{}".format(try_this))
        else:
            if '.' not in try_this:
                try_list.append("/{}/".format(try_this))
            else:
                try_list.append("/{}".format(try_this))

        for list in try_list:
            url = "{}{}".format(target, p.quote(list))
            url = delencode(url)
            
            try:
                headers = {
                    'User_Agent' : user_agent
                }
                res = requests.get(url, headers=headers)
                if len(res.text):
                    if res.status_code != 404:
                        if res.status_code == 200:
                            print("==================================================")
                            print("found : [{}] ==> {}".format(res.status_code, url))
                            print("==================================================")
                            if not os.path.isdir("result"):
                                os.mkdir("result")

                            with open("result/" + delschema(target) + ".txt", "a+") as ff:
                                ff.write(url+'\n')
                else: print(f'there is no data : {url}\n')

            except(reqe.HTTPError) as er:
                print("except", er)
                if hasattr(er.HTTPError, 'code') and er.HTTPError.code != 404:
                    print("!!! [{}] ==> {}".format(er.HTTPError.code, url))
        word = f.readline()
    f.close()
    
def brute_dir(word_queue, target, extensions=None):
    while not word_queue.empty():
            
        try_this = word_queue.get()
        try_list = []
        if extensions:
            if '.' not in try_this:
                if '/' == try_this:
                    try_list.append("{}".format(try_this))
                else:
                    try_list.append("/{}/".format(try_this))
                    for extension in extensions:
                        try_list.append("/{}{}".format(try_this, extension))
            else:
                try_list.append("/{}".format(try_this))
        else:
            if '.' not in try_this:
                try_list.append("/{}/".format(try_this))
            else:
                try_list.append("/{}".format(try_this))
                    
                
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
                        if res.status == 200:
                            print("==================================================")
                            print("found : [{}] ==> {}".format(res.status, url))
                            print("==================================================")
                            '''
                            for _ in try_list:
                                url2 = "{}{}".format(url, try_list)
                                res2 = http.request("GET", header=head, url = url2_)
                                
                                if len(res2.data):
                                    if res2.status != 404:
                                        if res2.status == 200:
                                            print("there is : {}".format(url2))
                            '''     
                else:
                    print(f'there is no data : {url}\n')
            #except Exception as e: print("error : ", e)
            
            
            except(e.URLError, e.HTTPError) as e:
                print("except", e)
                if hasattr(e.HTTPError, 'code') and e.HTTPError.code != 404:
                    print("!!! [{}] ==> {}".format(e.HTTPError.code, url))
            


if __name__ == "__main__":
    d_queue = create_wordlist(wl_file)
    target = input("target : ")
    print("brute_dir() starting...\n")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = [executor.submit(brute_dir, d_queue, target ,ext) for _ in range(10)]
        print("working...\n")
