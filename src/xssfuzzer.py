#!/bin/python3
import urllib3
import urllib.parse as p
import urllib.error as e
import argparse

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.77 Safari/537.36'

parser = argparse.ArgumentParser()
parser.add_argument('-u', action='store', dest='url', help='The URL to analyze')
parser.add_argument('-c', action='store', dest='cookies',
                    help='Space separated list of cookies',
                    nargs='+', default=[])
args = parser.parse_args()

url = args.url
