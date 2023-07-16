import getpass
import time
import re
import csv
import sys
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from prettytable import PrettyTable

options = Options()

# 必要に応じてoptionsを設定



sokutei_wait_time = float(input("測定周期を入力(単位：秒)："))

driver = webdriver.Chrome(options=options)
LOGIN_PAGE = "https://my.lightfx.jp/login"
TRADE_PAGE_URL= "https://fxtrader.lightfx.jp/express/rest/utility/cas?customerId=53877989"


driver.get(LOGIN_PAGE)
print("ログインして下さい")

#ログイン確認処理
for i in range(1000):
    time.sleep(2)
    if driver.title == "マイページ|LIGHT FX":
        print("ログイン確認成功")
        break
    else:
        pass


driver.get(TRADE_PAGE_URL)
time.sleep(2)

loopcount = 0
while True:
    start_time = time.perf_counter()
    loopcount+=1
    if driver.title.find("シンプルトレーダー|LIGHT FX")<0:
        print("ログイン失敗かも！ システムを終了します。")
        time.sleep(10)
        driver.quit()
        sys.exit()

    html = driver.page_source.encode('utf-8');soup = BeautifulSoup(html, "html.parser")
    connection_status =soup.find("li", class_="connection connected ember-view").get("data-original-title")
    if connection_status != "通信中":
        print("通信途絶")
        sys.exit()

    #日付と時間を取得する。    
    today = soup.find("li",id="date").text
    now_time = soup.find("li",id="time").text

    #維持率とかを確認する。
    line = soup.find_all("number")
    leverage_rasio = re.sub(r"[^\d.]", "",line[0].text)
    ijiritsu = re.sub(r"[^\d.]", "",line[1].text)
    junshisan =re.sub(r"[^\d.]", "",line[2].text)
    soneki = re.sub(r"[^\d.-]", "",line[3].text)


    names =[];buy_prices = [];sell_prices=[];spreads=[];buy_swaps=[];sell_swaps=[]
    pair_count = len(soup.find("div",class_="tbl-table").find_all("div",class_ = "tbl-row"))
    for i in range(pair_count):
        line =soup.find("div",class_="tbl-table").find_all("div",class_ = "tbl-row")[i].find_all("div",class_="tbl-cell")
        names.append(line[0].text.replace("\n",""))
        buy_prices.append(re.sub(r"[^\d.]", "",line[2].text))
        sell_prices.append(re.sub(r"[^\d.]", "",line[3].text))
        spreads.append(re.sub(r"[^\d.]", "",line[4].text))
        buy_swaps.append(line[7].text.replace("\n","").replace(" ",""))
        sell_swaps.append(line[8].text.replace("\n","").replace(" ",""))
        del line

    table = PrettyTable()
    show_data =[0,10,6,16] #0= USDJPY light   #10=USDJPY(Nom)   #6=MXNJPY(Light)    #16=MXNJPY(NOM)
    table.field_names= ["pair", "BUY","SELL","spread","BUY_SWAP","SELL_SWAP"]
    for i in show_data:
        table.add_row([names[i],buy_prices[i],sell_prices[i],spreads[i],buy_swaps[i],sell_swaps[i]])
    print(f"{today}  {now_time}")
    print(table,f"\nレバレッジ:{leverage_rasio}   維持率:{ijiritsu}   損益:{soneki}\n\n\n")
    
    
    if loopcount ==1:
        header_flag = not(os.path.isfile("\spread.csv"))
    else:
        header_flag = False
    with open(f".\spread.csv","a", newline="") as f:
        if header_flag ==True:
            csv.writer(f).writerow(["day","time","維持率(%)",*names])
        else:
            pass
        csv.writer(f).writerow([today,now_time,ijiritsu,*spreads])

    wait_time = start_time + sokutei_wait_time - time.perf_counter()
    if wait_time >= 0:
        time.sleep(wait_time)
    else:
        pass