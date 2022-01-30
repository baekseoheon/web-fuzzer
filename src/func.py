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
from bs4 import BeautifulSoup


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

                            with open("result/" + delschema(target) + "_dir_scan.txt", "a+") as ff:
                                ff.write(url+'\n')
                else: print(f'there is no data : {url}\n')

            except(reqe.HTTPError) as er:
                print("except", er)
                if hasattr(er.HTTPError, 'code') and er.HTTPError.code != 404:
                    print("!!! [{}] ==> {}".format(er.HTTPError.code, url))
        word = f.readline()

def web_scan(url):
    res = requests.get(url)
    print("==================================================")
    print("{} URL : {}".format(res.status_code, res.url))
    print("Headers : ", res.headers)
    print("cookies : ", res.cookies)
    print("==================================================")
    if not os.path.isdir("result"):
        os.mkdir("result")

    with open("result/"+delschema(url)+"_web_scan.txt", "a+") as ff:
        ff.write('[' + str(res.status_code) + '] ' + str(res.url) + '\n' + str(res.headers) +'\n' + str(res.cookies) + '\n\n')


def xss_scan(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    for formtag in soup.findAll('form'):
        print('Using' + formtag.get('method') + ' Method')
        if(formtag.get('method').upper() == 'GET'):
            with open('XSS_payload.txt', "r", errors="replace") as code:
                for i in code:
                    with open('result/' + delschema(url) + '.txt', "r", errors="replace") as xss:
                        for j in xss:
                            html = requests.get(j)
                            sp = BeautifulSoup(html, "html.parser")
                            for inputtag in sp.findAll('input'):
                                try:
                                    #user = user_agent
                                    header = {"User-Agent": user_agent}
                                    inputtagname = inputtag.get('name')
                                    payload = delencode(url + '/' + formtag.get('action') + '?' + inputtagname + "=" + i)
                                    req = requests.get(payload, headers=header)
                                    
                                    if i in req.text:
                                        #print("parameter vulnerable")
                                        print("Vulnerable payload find\t: " + req.url)
                                        with open("result_xss_scan" + delschema(url) + '_xss_get.txt', "a+") as rf:
                                            rf.write(payload+"\n")
                                    else:
                                        print("Trying\t => [" + req.url + "]")
                                except:
                                    pass
    print("there is no form tag")
    sys.exit(0)