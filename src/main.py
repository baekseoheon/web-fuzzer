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
from brute_dir import *

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
    
if __name__=='__main__':
    banner()
    specify_text_color()
    arg_parse_result = arg_parse()
    target = arg_parse_result.url
    wordlist_name = arg_parse_result.file
    
    if arg_parse_result.brute_flag:
        if wordlist_name:
            print("------------------------------")
            print('loading wordlist....')
            print("------------------------------\n")
            d_queue = create_wordlist(wordlist_name)
            print("------------------------------")
            print('loaded wordlist....')
            print("------------------------------\n")
        else:
            print("------------------------------")
            print("creating wordlist....")
            print("------------------------------\n")
            d_queue = create_wordlist(wl_file)
            print("------------------------------")
            print("created wordlist....")
            print("------------------------------\n")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            print("working...")
            result = [executor.submit(brute_dir, d_queue, target, ext) for _ in range(10)]
            
            print("It worked!\n")
            
    elif arg_parse_result.xss_flag:
        print("xss()")
        
    elif arg_parse_result.sql_flag:
        print("sql injection()")
        
    else:
        usage()
    
    
    
    