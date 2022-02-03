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
from selenium import webdriver
from seleniumrequests import Chrome

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
                    #else: print("can not find : ", url)
                else: print(f'there is no data : {url}\n')

            except(reqe.HTTPError) as er:
                print("except", er)
                if hasattr(er.HTTPError, 'code') and er.HTTPError.code != 404:
                    print("!!! [{}] ==> {}".format(er.HTTPError.code, url))
        word = f.readline()
    f.close()
def xss_scan(url):
    options = webdriver.ChromeOptions()
    options.add_argument('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.77 Safari/537.36')

    driver = webdriver.Chrome('./chromedriver', options=options)
    driver.implicitly_wait(time_to_wait=10)
    driver.get(url=url)
    
    src = driver.page_source
    soup = BeautifulSoup(src, "html.parser")

    for formtag in soup.find_all('form'):
        print(formtag)
        if (formtag.get('method').upper() == 'GET'):
            print("Using GET method")
            with open('xss_payload.txt', 'r', errors="error") as code:
                for i in code:
                    for inputtag in soup.find_all('input'):
                        try:
                            header = {"User-Agent": user_agent}
                            inputtagname = inputtag.get('name')
                            if formtag.get('action'):
                                action = formtag.get('action')
                                payload = delencode(url + '/' + action + '?' + inputtagname + '=' + i)
                                #res = requests.get(payload)
                                driver.get(url=payload)
                                current_url = driver.current_url
                                print(current_url)

                                try:
                                    alert = driver.switch_to_alert
                                    alert.accept()

                                    print("Vulnerable payload find\t: " + current_url)
                                    with open("result_xss_scan" + delschema(url) + '_xss_get.txt', "a+") as rf:
                                        rf.write(payload+"\n")
                                except: pass

                                '''
                                if i in res.text:
                                    #print("parameter vulnerable")
                                    print("Vulnerable payload find\t: " + res.url)
                                    with open("result_xss_scan" + delschema(url) + '_xss_get.txt', "a+") as rf:
                                        rf.write(payload+"\n")
                                else: print("Trying\t => [" + res.url + "]")
                                '''
                        except: pass
        elif (formtag.get('method').upper() == 'POST'):
            print("Using POST method")
            with open('xss_payload.txt', 'r', errors='error') as code:
                i = code.readline()
                print(i)
                #for i in code:
                for inputtag in soup.findAll('input'):
                    inputtagname = inputtag.get('name')
                    if inputtagname is None:
                        continue
                    data = {}
                    data[inputtagname] = i
                    #print("input tag name : {}, payload : {}".format(inputtagname, data[inputtagname]))
                    try:
                        header = {"User-Agent" : user_agent}
                        payload = delencode(url + '/' + formtag.get('action'))
                        print("payload ", payload)
                        rep = requests.post(payload, headers=header, data=data)
                        
                        if rep.status_code == 200:
                            print("Vulneranle Payload Find\t: " + rep.url)
                            with open("result_xss_scan/" + delschema(url) + '_xss_post.txt', "a+") as rf:
                                rf.write(payload + "\n" + inputtagname + ":" + i + '\n')
                        else:
                            print("Trying\t:", rep.url)
                    except: pass
    driver.close()

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
        ff.close()


    
