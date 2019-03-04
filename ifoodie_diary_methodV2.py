from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError
import requests
import re
import json

"""
首先順一下觀念吧 ！

定義方法 就像流程一樣

讓你不用重複寫一樣的東西

流程不一定要傳入物件或參數 也能運作 一個流程 你懂的

若要傳入物件或參數 那就要表示你要對這個物件 做一樣的動作

以這個例子來說

你想要一個完整的流程 丟入網址後 就會吐出 整理好的食記內容

還是要傳入一個 html 文字檔 就吐出 整理好的食記內容

這兩個要搞清楚
"""
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





