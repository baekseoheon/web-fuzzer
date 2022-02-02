from __future__ import print_function
from ast import arg
from re import X
import sys
import requests
import time
from pprint import pprint
from text_color import *
from banner import *
from arg_parse import *
from usage import *
#from func import *
from func_v2 import *

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
    
if __name__=="__main__":
    banner()
    specify_text_color()
    arg_parse_result = arg_parse()
    if arg_parse_result.url:
        target = arg_parse_result.url
    
    if arg_parse_result.file:
        wordlist_name = arg_parse_result.file
    else: wordlist_name = None    
    
    if arg_parse_result.brute_flag:
        if wordlist_name is not None:
            print("------------------------------")
            print('loading wordlist....')
            print("------------------------------\n")
            wordlist = wordlist_name
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
        print("xss")
        xss_scan(target)
        print("xss()")
        
    elif arg_parse_result.sql_flag:
        print("sql injection()")
    elif arg_parse_result.web_scan_flag:
        web_scan(target)
        
    else:
        usage()
    
    
    
    