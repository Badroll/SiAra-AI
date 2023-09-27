from flask import jsonify
from os import path
import hashlib
from datetime import datetime

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