import json
import os.path
import random
import re
import time

from bs4 import BeautifulSoup
import requests

main_url = 'https://moscow.birge.ru/catalog/'
page = requests.get(main_url)

with open(f'categories.html', 'w') as file:
    file.write(page.text)

with open(f'categories.html') as file:
    cat = file.read()

soup = BeautifulSoup(page.text, 'html.parser')

categoru = []
all_category = soup.find(class_='catalog_categories').find_all('a')
all_category = re.findall('href=[\'"]?([^\'" >]+)', str(all_category))
for i in all_category:
    # category = i.find_all(class_='category-container')
    folder_category = f'birge/data/{i.split("/")[-2]}'
    if os.path.exists(folder_category):
        pass
    else:
        os.mkdir(folder_category)

    url = 'https://moscow.birge.ru/catalog/rabota_predlagayu/'

    for i in range(1, 18):
        page = requests.get(url + f'?PAGEN_1={i}', allow_redirects=False)

        folder_name = f'{folder_category}/page_{i}'
        if os.path.exists(folder_name):
            print(folder_name + ' is exists')
        else:
            os.mkdir(folder_name)

        category_name = url.split('/')[-2]

        with open(f'birge/data/main.html', 'w') as file:
            file.write(page.text)

        with open(f'birge/data/main.html') as file:
            src = file.read()
        #
        soup = BeautifulSoup(src, "html.parser")
        posts = soup.find_all(class_='catalog_item')

        detail_urls = []
        posts_list = []
        for post in posts:
            detail_url = "https://moscow.birge.ru" + post.find(class_='href-detail').get('href')
            detail_urls.append(detail_url)

        for detail_url in detail_urls[:10]:
            page = requests.get(detail_url)
            post_id = detail_url.split('/')[-2]
            with open(f'{folder_name}/{post_id}.html', 'w') as file:
                file.write(page.text)
            #
            with open(f'{folder_name}/{post_id}.html') as file:
                src = file.read()
            #
            soup = BeautifulSoup(src, 'lxml')
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
                    'Наименование': detail_data_name,
                    'Лого URL ': detail_data_photo,
                    'Описание': detail_data_disc,
                    'Город': detail_data_city,
                    'Метро': detail_data_metro,
                    'Пользователь': detail_data_user,
                    'Номер': detail_data_number,
                    'Почта': detail_data_mail,
                }
            )
            time.sleep(random.randrange(2, 4))

        with open(f'{folder_category}/ads.json', 'a', encoding='utf-8') as file:
            json.dump(posts_list, file, indent=4, ensure_ascii=False)
