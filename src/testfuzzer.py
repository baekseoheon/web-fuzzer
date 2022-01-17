from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
csv_name = "main_all.csv"
csv_open = open(csv_name, "w+", encoding="utf-8")
csv_writer = csv.writer(csv_open)
csv_writer.writerow(("category", "drink", "image_url"))

driver = webdriver.Chrome(ChromeDriverManager().install())
crawling_url = "https://www.starbucks.co.kr/menu/drink_list.do"
driver.get(crawling_url)

full_html = driver.page_source
soup = BeautifulSoup(full_html, 'html.parser')
time.sleep(3)
categories = soup.select('#mCSB_1_container > li')
for i in range(2, len(categories)+1):
    element = driver.find_element_by_css_selector(f'#mCSB_1_container > li:nth-child({i})')
    category_name = element.text
    time.sleep(2)
    element.click()
    full_html = driver.page_source
    soup = BeautifulSoup(full_html, 'html.parser')
    titles = soup.select(f'#container > div.content > div.product_result_wrap.product_result_wrap01 > div > dl > dd:nth-child(2) > div.product_list > dl > dd:nth-child({(i-1)*2}) > ul > li > dl > dt > a > img')
    for i, title in enumerate(titles):
        print('title: ', title['alt'])
        print('original src: ', title['src'])
        print('image_url: ', title['src'].split('/')[4:])
        url = crawling_url + '/' + '/'.join(title['src'].split('/')[4:])