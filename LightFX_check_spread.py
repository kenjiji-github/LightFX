import time
import re
import csv
import sys
import os
import configparser
import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from prettytable import PrettyTable

import general.ambient as ambient

def AMBIENT_send_spreads(USDJPY, USDJPY_LIGHT, MXNJPY, MXNJPY_LIGHT,TRYJPY,TRYJPY_LIGHT,ZARJPY, ZARJPY_LIGHT):
    try:
        res =ambient.Ambient(AMBIENT_CHANNEL,AMBIENT_WRHITE_KEY).send(
            {"d1": float(USDJPY),
            "d2": float(USDJPY_LIGHT),
            "d3": float(MXNJPY),
            "d4": float(MXNJPY_LIGHT),
            "d5": float(TRYJPY),
            "d6": float(TRYJPY_LIGHT),
            "d7": float(ZARJPY),
            "d8": float(ZARJPY_LIGHT)},
            )
    except:
        print("error: cannot send data to ambient!")



if os.path.exists('config.ini'):
    config= configparser.ConfigParser()
    config.read('./config.ini', encoding="utf-8")
    AMBIENT_SEND_FLAG = config.getboolean("AMBIENT","AMBIENT_SEND_FLAG")
else:
    AMBIENT_SEND_FLAG = False
    
if AMBIENT_SEND_FLAG ==True:
    AMBIENT_SEND_MIN_TIME = 24*3600/3000 #24時間当たり3000発まで送れる
    AMBIENT_CHANNEL=config["AMBIENT"]["AMBIENT_CHANNEL"]
    AMBIENT_WRHITE_KEY=config["AMBIENT"]["AMBIENT_WRHITE_KEY"]
else:
    pass

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

if AMBIENT_SEND_FLAG ==True:
    post_ambient_sent_time = 0
    store_datas = []

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
    
    
    #1週目の時のみ max_spreadsにspreadの値をflootでコピーする
    if loopcount <= 1:
        max_spreads = [float(i) for i in spreads]
    else:
        pass
    
    count = 0
    table.field_names= ["pair", "BUY","SELL","now_spread","max_spread","BUY_SWAP","SELL_SWAP","delta_swap"]
    for i in show_data:
        #max_spreadsの値を更新
        max_spreads[i] = float(spreads[i]) if(float(spreads[i])> max_spreads[i]) else max_spreads[i]
        if (count := count +1)%2 ==1: #奇数行の時
            temp_swap = float(buy_swaps[i])
            delta_swap = ""
        else: #偶数行の時
            delta_swap = f"{temp_swap + float(sell_swaps[i]):.2f}"
            
        #tableに値を追加
        table.add_row([names[i],buy_prices[i],sell_prices[i],spreads[i],f"{max_spreads[i]:.2f}",buy_swaps[i],sell_swaps[i],delta_swap])
    print(f"{today}  {now_time}")
    print(table,f"\nレバレッジ:{leverage_rasio}   維持率:{ijiritsu}   損益:{soneki}\n\n\n")
    
    
    if loopcount ==1:
        header_flag = True
    else:
        header_flag = False
    
    now_date= datetime.datetime.now().strftime("%y%m%d")
    with open(f".\spread_{now_date}.csv","a", newline="") as f:
        if header_flag ==True:
            csv.writer(f).writerow(["day","time","維持率(%)",*names])
        else:
            pass
        csv.writer(f).writerow([today,now_time,ijiritsu,*spreads])

    if AMBIENT_SEND_FLAG ==True:
        now_datas =[float(spreads[10]),float(spreads[0]),float(spreads[16]),float(spreads[6]),float(spreads[15]),float(spreads[5]),float(spreads[17]),float(spreads[7])]
        if store_datas ==[]:
            store_datas = now_datas.copy()
        else:
            for i in range (len(now_datas)):
                store_datas[i] = max(store_datas[i], now_datas[i])
        
        #送信タイミングの時
        if (time.perf_counter() - post_ambient_sent_time > AMBIENT_SEND_MIN_TIME):
            post_ambient_sent_time= time.perf_counter()
            AMBIENT_send_spreads(*store_datas)
            store_datas = []
        else:
            pass
    wait_time = start_time + sokutei_wait_time - time.perf_counter()
    if wait_time >= 0:
        time.sleep(wait_time)
    else:
        pass