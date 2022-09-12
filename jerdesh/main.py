import json
import os.path
import random
import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True
driver = webdriver.Chrome('/Users/azizamakeeva/Downloads/chromedriver', options=options)

url = 'http://jerdesh.ru'
resp = requests.get(url)
soup = BeautifulSoup(resp.text, 'lxml')

categories = soup.find_all(class_='category')  # все категории
all_category = re.findall('href=[\'"]?([^\'" >]+)', str(categories))  # ссылка на все категории

for i in all_category:  # создаем папку с названием категории
    folder_category = f'data/{i.split("/")[-1]}'

    url = i  # ссылка на страницу всех обьявлений категории

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    pagen_count = soup.find(class_='counter-search').text
    pagen_count = re.search('из .*.(\d)', pagen_count).group()
    pagen_count = round(int(pagen_count.replace('из ', '')) / 40)  # 40 - кол-во обьявления на странице
    for i in range(1, pagen_count):
        print(f'Pagen={i}')
        driver.get(url + f'/{i}')
        page = driver.page_source  # страница обьявлений категории
        soup = BeautifulSoup(page, 'html.parser')
        folder_name = f'{folder_category}/page_{i}'

        posts = soup.find_all(class_='listing-card')
        detail_urls = []
        posts_list = []

        for post in posts:
            detail_url = post.find(class_='listing-thumb').get('href')
            detail_urls.append(detail_url)

        for detail_url in detail_urls:
            driver.get(detail_url)
            src = driver.page_source
            soup = BeautifulSoup(src, 'html.parser')
            content = soup.find(id='jarnama')

            try:
                title = content.find('h1').text
            except Exception:
                title = 'No'

            desc_content = content.find(id='description')
            try:
                desc = desc_content.find('p').text
            except Exception:
                desc = 'No'
            try:
                user = desc_content.find_all('span')[1].text
            except Exception:
                user = "Unknown"
            try:
                number = desc_content.find('a').text

            except Exception:
                number = "Unknown"

            location_content = soup.find(id='item_location')

            try:
                location = str((location_content.find_all('li')[0]).text.split(':')[1].strip())

            except Exception:
                location = "Unknown"
            try:
                images = []
                photo_content = content.find(class_='item-photos').find(class_='thumbs')
                content_images = photo_content.find_all('img')
                for image in content_images:
                    img = (image['src'])
                    images.append(img)
            except Exception:
                images = ['No photo']

            posts_list.append(
                {
                    'ad_name': title,
                    'logo_url': images,
                    'description': desc,
                    'user': user,
                    'phone_number': number,
                    'location': location,
                    'link': detail_url,

                }
            )
            # time.sleep(random.randrange(2, 4))

        with open(f'ads.json', 'a', encoding='utf-8') as file:
            json.dump(posts_list, file, indent=4, ensure_ascii=False)
