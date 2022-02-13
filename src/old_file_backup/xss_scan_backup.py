import sys, os, re, requests, websockets.client
import http.client as httplib
import urllib.parse as p 
import urllib.error as e
import requests.exceptions as reqe
from pdb import post_mortem
from cgitb import reset
from tabnanny import check
from telnetlib import EC
from termios import ECHOE
from more_itertools import value_chain
from bs4 import BeautifulSoup
from sympy import E
from requests_html import HTMLSession
from selenium import webdriver
from urllib.parse import urljoin



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
     
def xss_scan(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('--disable-gpu')
    options.add_argument('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.77 Safari/537.36')

    driver = webdriver.Chrome('./chromedriver', options=options)
    driver.implicitly_wait(time_to_wait=10)
    driver.get(url)
    
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
                            else: payload = delencode(url + '?' + inputtagname + '=' + i)

                                #res = requests.get(payload)
                            driver.get(payload)
                            current_url = driver.current_url
                                #print(current_url)

                            try:
                                alert = driver.switch_to.alert
                                alert.accept()

                                print("Vulnerable payload find\t: " + current_url)

                                if not os.path.isdir("result_xss_scan"):
                                    os.mkdir("result_xss_scan")

                                with open("result_xss_scan/" + delschema(url) + '_xss_get.txt', "a+") as rf:
                                    rf.write(payload+"\n")
                            except Exception as e1:
                                print("inside exepted ", e1)

                                '''
                                if i in res.text:
                                    #print("parameter vulnerable")
                                    print("Vulnerable payload find\t: " + res.url)
                                    with open("result_xss_scan" + delschema(url) + '_xss_get.txt', "a+") as rf:
                                        rf.write(payload+"\n")
                                else: print("Trying\t => [" + res.url + "]")
                                '''
                        except Exception as e:
                            print("excepted ", e)

        elif (formtag.get('method').upper() == 'POST'):
            print("Using POST method")
            with open('xss_payload.txt', 'r', errors='error') as code:
                #i = code.readline()
                #print(i)
                for i in code:
                    for inputtag in soup.find_all('input'):
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
                            rep = driver.request('POST', payload, data=data)
                            print(rep.content)
                            
                            if rep.content:
                                print(rep.content)
                                print("Vulneranle Payload Find\t: " + rep.url)


                                with open("result_xss_scan/" + delschema(url) + '_xss_post.txt', "a+") as rf:
                                    rf.write(payload + "\n" + inputtagname + ":" + i + '\n')
                            else:
                                print("Trying\t:", rep.url)
                            driver.quit()

                        #rep = requests.post(payload, headers=header, data=data)
                        #firefoxdriver = Firefox()
                        #res = firefoxdriver.request('POST', payload, data=data)

                        '''
                        alert = res.switch_to_alert()
                        print("alert", alert)
                        if alert:
                            alert.accept()

                            print("Vulnerable payload find\t: " + current_url)
                            with open("result_xss_scan" + delschema(url) + '_xss_get.txt', "a+") as rf:
                                rf.write(payload+"\n")
                                '''
                        '''
                        if rep.status_code == 200:
                            print("Vulneranle Payload Find\t: " + rep.url)
                            with open("result_xss_scan/" + delschema(url) + '_xss_post.txt', "a+") as rf:
                                rf.write(payload + "\n" + inputtagname + ":" + i + '\n')
                        else:
                            print("Trying\t:", rep.url)
                    
                        '''
                        except Exception as e:
                            print("POST Exception : ", e)
    driver.close()