import time
import requests
from bs4 import BeautifulSoup


print("LightFXスワップ確認ツール pwd kenjiji\n\n")


print("スワップ取得中……\n")
#データを取得する
res = requests.get("https://lightfx.jp/market/swap/")
soup = BeautifulSoup(res.text, "html.parser")

#CSSセレクターを使ってデータ取得する
day = soup.select("#symbol5 > div > table > tbody > tr:nth-child(1) > td:nth-child(1)")[0].text.replace("\t","").replace("\n","")
usdjpy_buy_swap = soup.select("#symbol5 > div > table > tbody > tr:nth-child(2) > td:nth-child(2)")[0].text
usdjpy_sell_swap = soup.select("#symbol1 > div > table > tbody > tr:nth-child(3) > td:nth-child(2)")[0].text
mxnjpy_buy_swap = soup.select("#symbol5 > div > table > tbody > tr:nth-child(2) > td:nth-child(9)")[0].text
mxnjpy_sell_swap = soup.select("#symbol1 > div > table > tbody > tr:nth-child(3) > td:nth-child(10)")[0].text

print("確認結果\n")
if usdjpy_buy_swap == usdjpy_sell_swap == mxnjpy_buy_swap == mxnjpy_sell_swap == '-':
    text = f"{day}\n今日はスワップ無し"
    print(text)

elif usdjpy_buy_swap == usdjpy_sell_swap == mxnjpy_buy_swap == mxnjpy_sell_swap == '公表前':
    text = f"{day}\nスワップ開示時間前, 18:00以降にスワップ確認して下さい。"
    print(text)
    
else:
    try:
        usdjpy_buy_swap = float(usdjpy_buy_swap)
        usdjpy_sell_swap = float(usdjpy_sell_swap)
        usdjpy_get_swap = round(usdjpy_buy_swap + usdjpy_sell_swap,1)

        mxnjpy_buy_swap = float(mxnjpy_buy_swap)
        mxnjpy_sell_swap = float(mxnjpy_sell_swap)
        mxnjpy_get_swap = round(mxnjpy_buy_swap + mxnjpy_sell_swap, 1)
        
        if usdjpy_get_swap > 0 and mxnjpy_get_swap > 0:
            print(day,"\nget_usd_swap",usdjpy_get_swap,"\nget_mxn_swap",mxnjpy_get_swap)
            
        else:
            print(day,"注意_スワップ逆転！","\nget_usd_swap",usdjpy_get_swap,"\nget_mxn_swap",mxnjpy_get_swap)
    except:
        print("プログラムエラーのためサイトで確認してくること")
        
print("\n\n10秒後にプログラム停止します")
time.sleep(10)