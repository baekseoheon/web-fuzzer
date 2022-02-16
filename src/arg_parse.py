import sys
from usage import *

def arg_parse():
    import argparse
    
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='Process some option')
        parser.add_argument('-B', '--dir-brute-force', action='store_true', dest='brute_flag', help='If you want to do a driectory brute foce attack on the url')
        parser.add_argument('-X', '--xss', action='store_true', dest='xss_flag', help='If you want to do xss attack on the url')
        parser.add_argument('-S', '--sql-injection', action='store_true', dest='sql_flag', help='If you want to do sql injection attack on the url')
        parser.add_argument('-s', '--web-scan', action='store_true', dest='web_scan_flag', help='If you want to scan the web')
        parser.add_argument('-u', '--url', '--target', action='store', dest='url', help='The URL to analyze')
        parser.add_argument('-m', '--max-total-string', action='store', dest='total_base_strings', help='Max total base strings, default 10')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0', help='check program version')
        parser.add_argument('-c', '--cookie', action='store', dest='cookies', help='Specify custom cookie values', nargs='+', default=[])
        parser.add_argument('-f', '--file', action='store', dest='file', help='specify file')
        parser.add_argument('-C', '--max-count', action='store', dest='max_tries', help='Max tries for string, default 7')
        parser.add_argument('-d', '--debug', action='store_true', dest='debug_mode', help='debug mode, default False')
        arg_parse_result = parser.parse_args()
        
        return arg_parse_result
    else:
        usage()
        sys.exit()