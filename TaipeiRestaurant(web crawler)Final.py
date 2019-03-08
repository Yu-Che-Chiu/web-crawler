from urllib.request import urlopen, Request, urlretrieve
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import requests
import json
import os
import random, time
from ifoodie_diary_methodV2 import *

# -- method
proxylist = [{"http": "37.187.120.123:80"},
             {"https": "206.189.36.198:8080"},
             {"https": "178.128.31.153:8080"},
             {"http": "167.114.180.102:8080"},
             {"http": "104.131.214.218:80"},
             {"http": "167.114.196.153:80"}]
header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

# 如何連線網頁
def get_connect(url):
    i = random.randint(0, len(proxylist) - 1)

    while True:

        try:
            resp = requests.get(url, headers=header, proxies=proxylist[i], timeout=120)
            resp.encoding = "utf-8"
            time.sleep(random.randint(1, 10) / 10)
            # logger.info("Request response", exc_info=True,extra={"url" : url, "time_use" : resp.elapsed.total_seconds(), "Response code" : resp.status_code, "proxy_use":proxylist[i]})

        except requests.exceptions.ConnectTimeout:
            # logger.warning("Connect Time out", exc_info=True)
            i = (i + 1) % len(proxylist)
            continue

        except requests.exceptions.ConnectionError:
            # logger.warning("Proxy Error", exc_info=True, extra={"proxy":proxylist[i],"url":url})

            i = (i + 1) % len(proxylist)
            continue
        if resp.status_code == requests.codes.ok:
            code = "HTTP response code = " + str(resp.status_code)
            # logger.info(code, exc_info=True, extra={"url": url})
            break
        if resp.status_code == 404:
            # logger.warning("This page is gone nowhere !", exc_info=True, extra={"url": url})

            break
        i = i + 1

    return resp
# 注意回傳的東西是個物件


# 主程式
'''
p.s. 進行網路爬蟲需要有一個urlopen進行連線，才可以執行網路爬蟲之任務。
     程式碼舉例： x = urlopen(url)
     但是，如果在短時間內執行爬蟲的任務過多，很有可能會被對方ban掉，這個時候需要撰寫一個proxy的方法才可以順利連線。
     程式碼舉例： 以我這次的爬蟲為例，需要連線proxy的方法為"get_connect(url)"，這時候連線的方法會變成 x = get_connect(url)
'''

page = 1

total = open('total_TaipeiCity(餐廳類別)', 'w+', encoding='utf-8')

while True:
    # result = []
    url = "https://ifoodie.tw/explore/%E5%8F%B0%E5%8C%97%E5%B8%82/list/%E6%97%A9%E5%8D%88%E9%A4%90?page=" + str(page)
    print("現在處理到第", url, "頁")

    '''
    <連線的方法1>
    try:
        response = urlopen(url)
    except HTTPError:
        print("Your mission is finished.")
        break
    html_food = BeautifulSoup(response)
    '''

    # <連線的方法2>，此方法是應用在"若是自己的連線被對方ban掉十，使用proxy連線繼續執行此任務。"
    try:
        response = get_connect(url)
    except HTTPError:
        print("Your mission is finished.")
        break
    html_food = BeautifulSoup(response.text)

    # global為全域變數
    global tpe_res_price, tpe_res_tel, tpe_res_score

    # 1F:爬取台北市之餐廳列表
    for r in html_food.find_all("div", class_="restaurant-item"):
        tpe_res_name = r.find("a", class_="title-text")
        tpe_res_address = r.find("div", class_="address-row")
        tpe_res_time = r.find("div", class_="info")

        # 因為網站上部分餐廳沒有寫出均消值、評分，所以要用try except讓它自動跳過，並且將空值自動寫"None"
        try:
            tpe_res_price = r.find("div", class_="avg-price").text
            tpe_res_score = r.find("div", class_="rating-star").text
            tpe_res_feedback = r.find("a", class_="review-count").text
        except AttributeError:
            tpe_res_price = None
            tpe_res_score = None
            tpe_res_feedback = None

        # 2F:因為第一層的網頁中，沒有顯示商家之電話號碼，需要連結至該商家之頁面以後才顯示，所以商家之電話在此處才會進行爬取。
        url2 = "https://ifoodie.tw" + tpe_res_name['href']

        ''''
        res2 = urlopen(url2)
        html_food2 = BeautifulSoup(res2)
        '''

        res2 = get_connect(url2)
        html_food2 = BeautifulSoup(res2.text)

        # 因為網站上部分餐廳沒有寫出電話，所以要用try except讓它自動跳過，並且將空值自動寫"None"
        try:
            # for tpe_res_tel2 in range(0, len(html_food2)):
            tpe_res_tel = html_food2.find_all("span", class_="detail").find("a", class_="jsx-3522274927").text
        except AttributeError:
            tpe_res_tel = None

        # 擷取經緯度
        tpe_res_latitude = html_food2.find("meta", property="place:location:latitude")['content']
        tpe_res_longitude = html_food2.find("meta", property="place:location:longitude")['content']

        # 3F:爬取使用者對餐廳回覆之相關資料

        url3 = "https://ifoodie.tw" + tpe_res_name['href']
        url_new = "https://ifoodie.tw/api/checkin/?restaurant_id=" + url3.split("/")[-1].split("-")[
            0] + "&offset=0&limit=200"
        res = requests.get(url_new)
        comment = []

        '''
        注意事項：
        # 1.透過google chrome的開發人員工具中，找到network的preview，尋找response。尋找底下的相關資料。
        # 2.在愛食記裡，從最外層的user中，找到display_name(指的是使用者之名稱)
        # 3.在愛食記裡，message指的是使用者回覆之訊息。
        '''
        j = json.loads(res.text, encoding="utf-8")
        print(j)
        for js in j:
            for a in j["response"]:
                try:
                    r = a["user"]["display_name"] + ":" + a["message"]

                    if ["display_name"] is None:
                        print("未知的作者")
                    else:
                        r = a["user"]["display_name"] + ":" + a["message"]
                        comment.append(r)
                except TypeError:
                       pass

                j_restaurant = a["restaurant"]
                print(j_restaurant)
                # product a dictionary
                res_name = j_restaurant["name"]
                res_address = j_restaurant["address"]
                res_time = j_restaurant["opening_hours"]
                # res_price = j_restaurant["price"]
                res_score = j_restaurant["rating"]
                # res_feedback = j_restaurant["feedback"]
                res_tel = j_restaurant["phone"]

        # 4F:爬取食記
        url_ifoodie = "https://ifoodie.tw/api/restaurant/" + url3.split("/")[-1].split("-")[0] + "/blogs/?offset=0&limit=10000"
        print(url_ifoodie)

        # ifoodie_response = requests.get(url_ifoodie)
        ifoodie_response = get_connect(url_ifoodie)
        j1 = json.loads(ifoodie_response.text, encoding="utf-8")

        diary_list = []  # build a list
        for js1 in j1["response"]:

            if js1["url"].find("ifoodie") == -1:
                pass
            else:
                print(js1["url"])
                url_food_diary = requests.get(js1["url"])
                soup = BeautifulSoup(url_food_diary.text)
                diary = get_ifoodie_diary(soup)

                diary_list.append({
                    "res_diary": diary

                })

                # comment.append(r)

                # res_diary = j1["res_diary"]

        # 第一個for迴圈裡面的所有的變數(tpe_res_name, tpe_res_address...到tpe_res_feedback)傳過來
        # json.loads(ifoodie_response.text)
        result = {
            "res_name": tpe_res_name.text,
            "res_addr": tpe_res_address.text,
            "res_lat": tpe_res_latitude,
            "res_long": tpe_res_longitude,
            "res_tel": tpe_res_tel,
            "res_time": tpe_res_time.text,
            "res_price": tpe_res_price,
            "res_score": tpe_res_score,
            "res_feedback": tpe_res_feedback,
            "comment": comment,
            "res_diary": diary_list
            # "res_lat_long": res_addr_latlong3
        }

        # json.dumps(result)
        print(result)

        total.write(json.dumps(result))
        total.write("\n")

    page = page + 1

# 檢視該網站列出之餐廳類別的總頁數多少(ex:總頁數14頁)，最後+1，讓程式暫停執行爬蟲。即可執行完成任務，否則會進入無窮迴圈。
    if page == 41 :
        break
