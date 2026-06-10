import requests

TOKEN = "8804329666:AAFDJW60KQLEt3CHYJTMDYCdl_fjdhE0Cnk"

def get_chat_id():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    resp = requests.get(url)
    print("Wyślij wiadomość do bota, potem uruchom ponownie ten skrypt")
    print(resp.json())

if __name__ == "__main__":
    get_chat_id()