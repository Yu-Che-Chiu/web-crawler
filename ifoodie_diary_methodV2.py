from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError
import requests
import re
import json


def get_ifoodie_diary(soup):

    # 傳入 經過BeautifulSoup 處理的 soup
    # 若出現亂碼情況 請在requests.get()之後
    # 加入encoding = 'utf-8'
 
    ifoodie_diary = soup.find("div", class_="post-content")
    removes = ifoodie_diary.find_all("script")
    for remove in removes:
        remove.extract()

    removes = ifoodie_diary.find_all("ins")
    for remove in removes:
        remove.extract()

    removes = ifoodie_diary.find_all("a")
    for remove in removes:
        remove.extract()

    ifoodie_diary = re.sub(r"\W+", "", ifoodie_diary.text)

    return ifoodie_diary


def get_ifoodie_image_urls(soup):

    # 傳入 BeautifulSoup 處理後的 soup

    # 此方法回傳 Urls List
    import re
    ifoodie_diary = soup.find("div", class_="post-content")
    images_url = []
    pattern = r"http\://farm2*"
    images = ifoodie_diary.find_all("img")
    for image in images:
        if re.match(pattern, image["src"]):
            images_url.append(image["src"])

    return images_url





