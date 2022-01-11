#!/bin/python3

import os
import queue
import threading
import urllib3
import urllib.parse as p 
import urllib.error as e

threads = 5
target = ''
# wordlist_file
wl_file = 'wordlist.txt'
ext = [".php", ".txt"]
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.77 Safari/537.36'
#queue_data = []


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

    
'''
def GetItemList(q):
    n = q.qsize()
    while n > 0:
        queue_data.append(q.get())
        n -= 1
'''

'''
f = open("word_test.txt", 'a+')
word = create_wordlist(wl_file)
while word.qsize() > 0:
    f.write(str(word.get())+'\n')
f.close
'''

def brute_dir(word_queue, extensions=None):

    while not word_queue.empty():
        try_this = word_queue.get()
        try_list = []

if __name__ == __main__:
    target = input()
