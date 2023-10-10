from flask import jsonify
from os import path
import hashlib
from datetime import datetime

TOKEN = "6353387757:AAHarFsMOrHwVg__9dGiEVOnal7_PGpPbuU"
chat_id = "-1001986787293"

def composeReply(status, message, payload = None):
    reply = {}
    reply["SENDER"] = "SIARAI"
    reply["STATUS"] = status
    reply["MESSAGE"] = message
    reply["PAYLOAD"] = payload
    return jsonify(reply)

ALLOWED_EXTENSION = set(["png", "jpg", "jpeg"])
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSION

def saveFile(file):
    try:
        #filename = str(datetime.now()).replace(":", "-") + (file.filename)
        filename = hashlib.md5(str(datetime.now()).encode('utf-8')).hexdigest() + "." + str(file.filename.rsplit(".", 1)[1].lower())
        basedir = path.abspath(path.dirname(__file__))
        file.save(path.join(basedir, "uploads", filename))
        return filename
    except TypeError as error : return [False, "Save file failed [" + error]

def send_telegram(msg):
    import requests
    # TOKEN = "6353387757:AAGMlehtqLbKopD1jDZl6FYehHOMoxrdxp4"
    # chat_id = "-4069351784"
    message = msg
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).json()) # this sends the message

def send_telegram_photo(file):
    import requests

    # Token bot Telegram Anda
    # TOKEN = "6353387757:AAGMlehtqLbKopD1jDZl6FYehHOMoxrdxp4"

    # # Chat ID tempat Anda ingin mengirim gambar
    # chat_id = "-4069351784"

    # Path ke gambar yang ingin Anda kirim
    path_to_image = file

    # URL API Telegram untuk mengirim gambar
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    # Membuat objek data yang berisi token bot, chat ID, dan gambar
    data = {
        "chat_id": chat_id,
    }

    # Membuka file gambar dan mengirimnya sebagai bagian dari permintaan POST
    with open(path_to_image, "rb") as image_file:
        files = {"photo": image_file}
        response = requests.post(url, data=data, files=files)

    # Cek respon dari API Telegram
    print(response.json())