#!/bin/python3

import sys, os, re, queue, requests, time, urllib3, websockets.client, concurrent.futures
import http.client as httplib
import urllib.parse as p 
import urllib.error as e
import requests.exceptions as reqe
from distutils import errors
from pdb import post_mortem
from bs4 import BeautifulSoup
from selenium import webdriver
from seleniumrequests import Chrome
from urllib.parse import urljoin
from requests_html import HTMLSession

wl_file = 'wordlist.txt'
ext = [".php", ".txt"]
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.77 Safari/537.36'

def make_url(url):
    try:
        # 사용자가 http 또는 https를 빼놓고 입력했을 때
        if ("http" not in url) and ("https" not in url):
            url = "http://" + str(url)
            #print("if() ",url)
        # 사용자가 https를 붙혔을 때
        elif "https" in url:
            url = "http://" + str(url[8:])
            # print("elif() ",url)
        # 사용자가 http를 붙혔을 때
        else: pass # print(url)

        #https에 접속 가능한지 여부를 판단하기 위함
        httpsurl = "https://" + str(url[7:])
        #print(httpsurl)
        r = requests.request("GET", httpsurl, timeout=2)

        # https에 성공적으로 접속했을 때
        if(r.status_code == 200) or (r.status_code == 302):
            url = "https://" + str(url[7:])
            #print(url)
        # 리다이렉트 되었을 때
        elif r.status_code == 301:
            loc = urlparse(httpsurl)
            url = loc.scheme + '://' + loc.netloc
            #print(url)
        return url
    except Exception: return url

def get_cookie(url):
    r = requests.get(url)
    
    if r.cookies:
        for cookie in r.cookies:
            cookies = {cookie.name: cookie.value}
        #print("cookie : ", cookies)
        return cookie
    else: return False

def make_webdriver(url):
    try:
        options = webdriver.ChromeOptions()
        option_value = ["headless", "window-size=1920x1080", "disable-gpu", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.77 Safari/537.36"]
        for _ in option_value:
            options.add_argument(_)
        driver = webdriver.Chrome("./chromedriver", options=options)
        driver.implicitly_wait(3)
        driver.set_page_load_timeout(3)
        driver.get(url)

        return driver
    except Exception:
        driver.quit()
        return False

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
                            if not os.path.isdir("result_dir_scan"):
                                os.mkdir("result_dir_scan")

                            with open("result_dir_scan/" + delschema(target) + "_dir_scan.txt", "a+") as ff:
                                ff.write(url+'\n')
                    #else: print("dont find : ", url)
                else: print(f'there is no data : {url}\n')

            except(reqe.HTTPError) as er:
                print("except", er)
                if hasattr(er.HTTPError, 'code') and er.HTTPError.code != 404:
                    print("!!! [{}] ==> {}".format(er.HTTPError.code, url))
        word = f.readline()
    f.close()

def find_all_links(soup):
    href = []
    for a in soup.find_all('a'):
        href.append(a.attrs.get('href'))
    return href

def find_tag(url, tag):
    # 세션 open
    session = HTMLSession()
     # driver.get()과 동일한 기능
    r = session.get(url)
    # 자바스크립트로 구성된 페이지를 html로 푼다
    r.html.render()

    soup = BeautifulSoup(r.html.html, "html.parser")
    tags = soup.find_all(tag)
    
    return tags

def find_all_form(soup):
    formtag = soup.find_all("form")
    return formtag

# 수정 필요
def get_forms_detail(forms):
    for form in forms:
        action = form.attrs.get("action").lower()
        method = form.attrs.get("method").lower()
        for input_tag in form.find_all("input"):
            input_tag_value = ""
            input_tag_type = input_tag.attrs.get("type")
            input_tag_name = input_tag.attrs.get("name")

def get_form_details(form):
    
    header = {"User-Agent": user_agent}

    action = form.attrs.get("action").lower()
    method = form.attrs.get("method").lower()
    
    details = {}
    inputs = []

    for input_tag in form.find_all("input"):
        
        input_tag_value = ""

        # input 태그 내의 type 값을 가져올 수 있다면 
        if input_tag.attrs.get("type"):
            input_tag_type = input_tag.attrs.get("type")
        else: input_tag_type = None

        # input 태그 내의 name 값을 가져올 수 있다면 
        if input_tag.attrs.get("name"):
            input_tag_name = input_tag.attrs.get("name")
        else: input_tag_name = None

        # input 태그 내의 pattern 값을 가져올 수 있다면 
        if input_tag.attrs.get("pattern"):
            pattern = input_tag_pattern = input_tag.attrs.get("pattern")
        else: pattern = input_tag_pattern = None

        # type의 값이 hidden이라면
        if input_tag_type == "hidden":
            # input 태으 내의 value 값을 가져 올 수 있다면
            if input_tag.attrs.get("value"):
                input_tag_value = input_tag.attrs.get("value")
            else: input_tag_value = None

        #inputs의 0번째에 type와 name value pattern 값 넣기
        inputs.append({"type":input_tag_type, "name":input_tag_name, "value":input_tag_value, "pattern":input_tag_pattern})

        details["action"] = action
        details["method"] = method
        details["inputs"] = inputs

        return details

def submit(form_details, url, payload, user_agent, cookies):
    if form_details["action"] != "None":
        target = urljoin(url, form_details["action"])
    else: target = url

    inputs = form_details["inputs"]
    data = {}
    for input in inputs:
        input["value"] = payload
        
        if input["type"] == "email":
            input["value"] = "abc@abc.com"

        input_name = input.get("name")
        input_value = input.get("value")
        if input_name and input_value:
            data[input_name] = input_value
        
        session = requests.Session()
        headers = {'User-Agent':user_agent}
        session.headers.update(headers)

    if form_details["method"] == "post":
        if cookies:
            return requests.post(target, data=data, cookies=cookies)
        else:
            return requests.post(target, data=data)
    else:
        if cookies:
            return requests.get(target, params=data, cookies=cookies)
        else:
            return requests.get(target, params=data)

def xss_scan(url):
    
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.77 Safari/537.36'
    cookies = {}
    redirect = False

    url = make_url(url)
    
    # url에 접속
    driver = make_webdriver(url)
    
    # url에 접속한 뒤 html 파싱하기 위함
    src = driver.page_source
    soup = BeautifulSoup(src, "html.parser")

    if driver.get_cookies():
        for cookie in driver.get_cookies():
            cookies[cookie.name] = cookie.value
        print(cookies)
    else: cookies = False
    
    # 링크들의 페이지를 파싱하기 위함
    other_soup = []

    # 페이지 내의 모든 링크 가져오기
    links = find_all_links(soup)
    
    '''
    if links:
        for link in links:
            # Url과 link 부분 합쳐서 요청
            other_url = urljoin(url, link)
            r = requests.get(other_url)
            
            other_driver = make_webdriver(other_url)
            other_src = other_driver.page_source
            
            if r.status_code == 200:
                other_soup.append(BeautifulSoup(r.content, "html.parser"))
    '''

    forms = find_all_form(soup)
    with open("xss_payload.txt", 'r') as payload_file:
        payload_data = payload_file.readlines()
        payload_file.close()
        try:
            for payload in payload_data:
                for form in forms:

                    form_details = get_form_details(form)
                    
                    request_result = submit(form_details, url, payload, user_agent, cookies)

                    if request_result.history:
                        if str(request_result[0])[11:14] == "302":
                            redirect = True
                    html_content = submit(form_details, url, payload, user_agent, cookies).content.decode()

                    soup = BeautifulSoup(html_content, "html.parser")
                    elem = [soup.get_text()]

                    # payload가 페이지 내의 데이터에 삽입이 되어 있는지 확인
                    matches = [match for match in elem if payload in match]

                    if redirect:
                        check_stored = requests.get(url)
                        redirect = False
                        soup = BeautifulSoup(check_stored.text, "html.parser")
                        if payload in check_stored.text:
                            print("[*] Input stored triggered on %s" % url)
                            print("Successful Payload : %s" % payload)
                            is_vulnerable = True
                        else: print("No input stored triggered")
                    
                    
                    if payload in html_content:
                        url = url.replace("\n", "")
                        print("==============================")
                        print("[*] XSS detected on %s\n" % url)
                        print("Successful payload is : %s" % payload)
                        print("form info : %s" % form_details)
                        print("==============================\n")
                        
                        if not os.path.isdir("result_xss_scan"):
                            os.mkdir("result_xss_scan")

                        with open("result_xss_scan/" + delschema(url) + '_xss_scan.txt', "a+") as rf:
                            rf.write(payload+"\n")
                        is_vulnerable = True
                    elif matches:
                        print("no xss point found ....")
                    else:
                        print("no xss point found .....")

            return is_vulnerable
        except Exception as e:
            print(e)
            pass

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