import requests
import time
import configparser

config= configparser.ConfigParser()
config.read('./config.ini', encoding="utf-8")
access_token = config["LINE"]["access_token"]

#LINE notify送信コマンド
def send_line(message):
    # data
    send_text = message
    text = {"message": f"{send_text}"}
    # header
    headers = {"Authorization": f"Bearer {access_token}"}
    # send massage
    requests.post("https://notify-api.line.me/api/notify", data=text, headers=headers)

if __name__ == '__main__':
    print("LINE 送信プログラム")
    
    try:
        message = input("送信するテキスト内容：")
        send_line(message)
        
                                    
    except:
        print("\n動作終了")
        time.sleep(2)