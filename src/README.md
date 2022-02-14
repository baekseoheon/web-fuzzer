# install python package

- using `requirements.txt`

```bash
pip3 install -r requirements.txt
```

- using `pip3 install`

```bash
pip3 install pyfiglet
pip3 install selenium
pip3 install websockets
pip3 install requests
pip3 install bs4
pip3 install requests_html
pip3 install numpy
pip3 install treelib
```

---

## install chrome in linux

프로그램을 실행하려면 chrome이 설치되어 있어야 한다.

```bash
# chrome deb 파일 다운로드
1. wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# chrome 설치
2. apt install ./google-chrome-stable_current_amd64.deb

# 버전 확인
3. google-chrome --version
```

## install chrome in linux

위 install chrome in linux에서 `gooloe-chrome --version` 명령어를 통해 출력된 버전과 동일한 chromedriver를 다운로드 해야 한다.

Chromedriver url : [[https://chromedriver.chromium.org/](https://chromedriver.chromium.org/)]([https://chromedriver.chromium.org/](https://chromedriver.chromium.org/))

```bash
# 특정 버전 chromedriver 다운로드 할 때
wget https://chromedriver.storage.googleapis.com/98.0.4758.80/chromedriver_linux64.zip
```

---

## Usage

```bash
#help
python3 main.py -h

# directory Brute force
python3 main.py -B -u [URL]

# XSS scan
python3 main.py -X -u [URL]

# SQL Fuzz
python3 main.py -S -u [URL]

# web scan
python3 main.py -s -u [URL]

# specify file
python3 main.py -f [filename]

```

---