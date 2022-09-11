import json
import random
import re
import time

import requests
from bs4 import BeautifulSoup

main_url = 'https://moscow.birge.ru/catalog/'
page = requests.get(main_url)

soup = BeautifulSoup(page.text, 'html.parser')

all_category = soup.find(class_='catalog_categories').find_all('a')
all_category = re.findall('href=[\'"]?([^\'" >]+)', str(all_category))
page_from = 1  # пагинация с n-ой страницы
page_to = 2  # пагинация до n-ой страницы
for i in all_category:
    folder_category = f'birge/data/{i.split("/")[-2]}'

    url = 'https://moscow.birge.ru/catalog/rabota_predlagayu/'

    for i in range(page_from, page_to):
        page = requests.get(url + f'?PAGEN_1={i}', allow_redirects=False)

        soup = BeautifulSoup(page.text, "html.parser")
        posts = soup.find_all(class_='catalog_item')

        detail_urls = []
        posts_list = []
        for post in posts:
            detail_url = "https://moscow.birge.ru" + post.find(class_='href-detail').get('href')
            detail_urls.append(detail_url)

        for detail_url in detail_urls:
            page = requests.get(detail_url)
            post_id = detail_url.split('/')[-2]

            soup = BeautifulSoup(page.text, 'lxml')
            detail_data = soup.find(class_='add_content')
            try:
                detail_data_photo = "https://moscow.birge.ru" + detail_data.find(
                    class_='main_photo fancybox-buttons').find(
                    'img').get('src')
            except Exception as ex:
                detail_data_photo = ' No logo'
            try:
                detail_data_name = detail_data.find(class_='name_ads').text

            except Exception as ex:
                detail_data_name = 'No name'

            try:
                detail_data_disc = detail_data.find(class_='ads_field').text

            except Exception as ex:
                detail_data_disc = 'No discription'

            try:
                detail_data_city = detail_data.find(class_='city-date').text
                detail_data_contacts = detail_data.find('div', class_='contact').text
                detail_data_metro = (detail_data_contacts[11:].split('\n')[2])
                detail_data_user = (detail_data_contacts[11:].split('\n')[0])
                detail_data_mail = (detail_data_contacts[11:].split('\n')[3])
            except Exception as ex:
                detail_data_city = 'Unknown'

            try:
                detail_data_number = "https://moscow.birge.ru" + detail_data.find(class_='dont_copy_phone').get('src')

            except Exception as ex:
                detail_data_number = 'No contacts'

            posts_list.append(
                {
                    'ad_name': detail_data_name,
                    'logo_url': detail_data_photo,
                    'description': detail_data_disc,
                    'city': detail_data_city,
                    'metro': detail_data_metro,
                    'user': detail_data_user,
                    'phone_number': detail_data_number,
                    'email': detail_data_mail,
                    'link': detail_url,
                }
            )
            time.sleep(random.randrange(2, 4))

        with open(f'birge/data/ads.json', 'a', encoding='utf-8') as file:
            json.dump(posts_list, file, indent=4, ensure_ascii=False)
