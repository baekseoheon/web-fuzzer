from __future__ import print_function
from ast import arg
from re import X
import sys
import requests
import time
import os
from pprint import pprint
from text_color import *
from banner import *
from arg_parse import *
from usage import *
from func import *
from sql_fuzz_func import *
import logging

if sys.version > '3':
    import urllib.parse as urlparse
    import urllib.parse as urllib
else:
    import urlparse
    import urllib
    
try:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()

except:
    pass

wl_file = 'wordlist.txt'
ext = [".php", ".txt"]
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.77 Safari/537.36'

url = "http://127.0.0.1/login/"
total_base_strings = 10
max_tries = 7
file = "Tools/Database/odds.json"
debug_mode = False

if __name__=="__main__":
    banner()
    specify_text_color()
    arg_parse_result = arg_parse()
    if arg_parse_result.url:
        target = arg_parse_result.url
    
    if arg_parse_result.file:
        file_name = arg_parse_result.file
    else: file_name = None    
    
    if arg_parse_result.brute_flag:
        if file_name is not None:
            print("------------------------------")
            print('loading wordlist....')
            print("------------------------------\n")
            wordlist = file_name
            #d_queue = create_wordlist(wordlist_name)
            print("------------------------------")
            print('loaded wordlist....')
            print("------------------------------\n")
        else:
            print("------------------------------")
            print("creating wordlist....")
            print("------------------------------\n")
            wordlist = wl_file
            #d_queue = create_wordlist(wl_file)
            print("------------------------------")
            print("created wordlist....")
            print("------------------------------\n")
        dir_scan(target, wordlist, ext)
        '''
        with concurrent.futures.ThreadPoolExecutor() as executor:
            print("working...")
            result = [executor.submit(brute_dir, d_queue, target, ext) for _ in range(10)]
        '''    
    elif arg_parse_result.xss_flag:
        xss_scan_v2(target)
        
    elif arg_parse_result.sql_flag:
        if not os.path.isdir("logs"):
            os.mkdir("logs")
            if not os.path.isfile("logs/fuzzer.log"):
                f = open("logs/fuzzer.log", 'w')
                f.close()
        init_args()
        sql_fuzz() 
        
    elif arg_parse_result.web_scan_flag:
        web_scan(target)
        
    else:
        usage()
    
    
    
    