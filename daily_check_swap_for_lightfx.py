import sys
import requests
from bs4 import BeautifulSoup


args = sys.argv


def send_line_notify(notification_message):
    line_notify_token = ${your_credential}
    line_notify_api = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {line_notify_token}"}
    data = {"message": f"message: {notification_message}"}
    requests.post(line_notify_api, headers=headers, data=data)


print("Daily LightFXスワップ確認ツール起動・・・\n\n")

res = requests.get("https://lightfx.jp/market/swap/")
soup = BeautifulSoup(res.text, "html.parser")

day = (
    soup.select("#symbol5 > div > table > tbody > tr:nth-child(1) > td:nth-child(1)")[0]
    .text.replace("\t", "")
    .replace("\n", "")
)
usdjpy_buy_swap = soup.select("#symbol5 > div > table > tbody > tr:nth-child(2) > td:nth-child(2)")[0].text
usdjpy_sell_swap = soup.select("#symbol1 > div > table > tbody > tr:nth-child(3) > td:nth-child(2)")[0].text
mxnjpy_buy_swap = soup.select("#symbol5 > div > table > tbody > tr:nth-child(2) > td:nth-child(9)")[0].text
mxnjpy_sell_swap = soup.select("#symbol1 > div > table > tbody > tr:nth-child(3) > td:nth-child(10)")[0].text

if usdjpy_buy_swap == usdjpy_sell_swap == mxnjpy_buy_swap == mxnjpy_sell_swap == "-":
    send_line_notify("スワップ無しの日です")
elif usdjpy_buy_swap == usdjpy_sell_swap == mxnjpy_buy_swap == mxnjpy_sell_swap == "公表前":
    send_line_notify("公表前のようです、時間を確認してください")
else:
    try:
        usdjpy_buy_swap = float(usdjpy_buy_swap)
        usdjpy_sell_swap = float(usdjpy_sell_swap)
        usdjpy_get_swap = round(usdjpy_buy_swap + usdjpy_sell_swap, 1)
        total_usdjpy_get_swap = usdjpy_get_swap * int(args[1])

        mxnjpy_buy_swap = float(mxnjpy_buy_swap)
        mxnjpy_sell_swap = float(mxnjpy_sell_swap)
        mxnjpy_get_swap = round(mxnjpy_buy_swap + mxnjpy_sell_swap, 1)
        total_mxnjpy_get_swap = mxnjpy_get_swap * int(args[2])

        if total_usdjpy_get_swap > 0 and total_mxnjpy_get_swap > 0:
            send_line_notify(
                "\n今日は"
                + day
                + "です\n明日の獲得swapは\nUSD/JPYが"
                + str(total_usdjpy_get_swap)
                + "円\nMXN/JPYが"
                + str(total_mxnjpy_get_swap)
                + "\n円になります"
            )
        else:
            send_line_notify(
                "\n今日は"
                + day
                + "です\n獲得swapがマイナスで\nUSD/JPYが"
                + str(total_usdjpy_get_swap)
                + "円\nMXN/JPYが"
                + str(total_mxnjpy_get_swap)
                + "\n円になります\n両建て解消するかご検討ください"
            )
    except:
        send_line_notify("予期せぬエラーが発生しました、直接サイトご確認ください")
        send_line_notify("https://lightfx.jp/market/swap/")

print("・・・Daily LightFXスワップ確認ツール終了\n\n")
