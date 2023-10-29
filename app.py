from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from PIL import Image, ImageFilter
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.lite.python.interpreter import Interpreter
import os
import json

import algorithm
import helper
import env

app = Flask(__name__, template_folder="view", static_folder="lib")
app.config["JSON_SORT_KEYS"] = False
app.secret_key = "siara-app123"
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/*": {"origins": "*"}})
log = ""

@app.route("/tes", methods = ["GET", "POST"])
def tes():
    import requests
    message = "testing"
    url = f"https://api.telegram.org/bot{env.TOKEN}/sendMessage?chat_id={env.chat_id}&text={message}"
    print(requests.get(url).json()) # this sends the message
    return "y"

@app.route("/aksara2latin", methods = ["GET", "POST"])
def aksara2latin():
    global log
    file = request.files["image"]
    if "image" not in request.files: return helper.composeReply("ERROR", "Gagal memuat file #1")
    if file.filename == "": return helper.composeReply("ERROR", "Gagal memuat file #2")
    if not (file and helper.allowed_file(file.filename)): 
        return helper.composeReply("ERROR", "Gagal memuat file #3")
    filename = helper.saveFile(file)
    currentpath = "uploads//"
    filepath = currentpath + filename
    labeled_filepath = currentpath + "labeled-" + filename
    resized_filepath = currentpath + "resized-" + filename

    def sort_objects_by_horizontal(detections):
        # Mengurutkan objek berdasarkan koordinat x dari centroid
        sorted_objects = sorted(detections, key=lambda x: (x[2] + x[4]) / 2)  # Menggunakan koordinat x dari centroid
        return sorted_objects

    def sort_objects_by_vertical(detections):
        # Mengurutkan objek berdasarkan koordinat y dari centroid
        sorted_objects = sorted(detections, key=lambda x: (x[3] + x[5]) / 2)  # Menggunakan koordinat y dari centroid
        return sorted_objects

    def detect_images(modelpath, imgpath, lblpath, min_conf=0.5, savepath='/content/results', txt_only=False):
        global log 
        with open(lblpath, 'r') as f:
            labels = [line.strip() for line in f.readlines()]

        interpreter = Interpreter(model_path=modelpath)
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        height = input_details[0]['shape'][1]
        width = input_details[0]['shape'][2]

        log += "\ninput_details:"
        log += f"\n{height} {width}\n"

        float_input = (input_details[0]['dtype'] == np.float32)

        input_mean = 127.5
        input_std = 127.5

        gambar = Image.open(imgpath)
        gambar = gambar.convert('L')
        threshold = 128  # Nilai ambang batas, sesuaikan sesuai kebutuhan
        gambar = gambar.point(lambda x: 0 if x < threshold else 255, '1')
        gambar.save(imgpath)

        image = cv2.imread(imgpath)
        #image = cv2.resize(image, (2000, 1500))
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imH, imW, _ = image.shape
        # image_rgb = cv2.resize(image_rgb, (2000, 1126))
        # cv2.imwrite("uploads//resized-1-" + filename, image_rgb)
        image_resized = cv2.resize(image_rgb, (width, height))
        input_data = np.expand_dims(image_resized, axis=0)

        cv2.imwrite(resized_filepath, image_resized)

        log += "\noriginal image shape:"
        log += f"\n{image.shape}\n"

        log += "\nresized image shape:"
        log += f"\n{image_resized.shape}\n"

        if float_input:
            input_data = (np.float32(input_data) - input_mean) / input_std

        interpreter.set_tensor(input_details[0]['index'],input_data)
        interpreter.invoke()

        boxes = interpreter.get_tensor(output_details[1]['index'])[0] # Bounding box coordinates of detected objects
        classes = interpreter.get_tensor(output_details[3]['index'])[0] # Class index of detected objects
        scores = interpreter.get_tensor(output_details[0]['index'])[0] # Confidence of detected objects

        detections = []

        for i in range(len(scores)):
            if ((scores[i] > min_conf) and (scores[i] <= 1.0)):
                ymin = int(max(1,(boxes[i][0] * imH)))
                xmin = int(max(1,(boxes[i][1] * imW)))
                ymax = int(min(imH,(boxes[i][2] * imH)))
                xmax = int(min(imW,(boxes[i][3] * imW)))

                cv2.rectangle(image, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

                object_name = labels[int(classes[i])]
                label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv2.rectangle(image, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                cv2.putText(image, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
                detections.append([object_name, scores[i], xmin, ymin, xmax, ymax])
        
        sorted_horizontal_objects = sort_objects_by_horizontal(detections)

        if txt_only == False:
            image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
            cv2.imwrite(labeled_filepath, image)

        elif txt_only == True:
            image_fn = os.path.basename(imgpath)
            base_fn, ext = os.path.splitext(image_fn)
            txt_result_fn = base_fn +'.txt'
            txt_savepath = os.path.join(savepath, txt_result_fn)

            with open(txt_savepath,'w') as f:
                for detection in detections:
                    f.write('%s %.4f %d %d %d %d\n' % (detection[0], detection[1], detection[2], detection[3], detection[4], detection[5]))

        return sorted_horizontal_objects

    PATH_TO_IMAGES = filepath 
    PATH_TO_MODEL = 'model/custom_model_lite4/detect.tflite'   # Path to .tflite model file
    PATH_TO_LABELS = 'model/labelmap.txt'   # Path to labelmap.txt file
    min_conf_threshold=0.01

    # PATH_TO_IMAGES = filepath 
    # PATH_TO_MODEL = 'model/custom_model_lite9/detect.tflite'   # Path to .tflite model file
    # PATH_TO_LABELS = 'model/labelmap_single.txt'   # Path to labelmap.txt file
    # min_conf_threshold=0.01

    log += "\nmodel : " + PATH_TO_MODEL + "\n"
    
    objects = detect_images(PATH_TO_MODEL, PATH_TO_IMAGES, PATH_TO_LABELS, min_conf_threshold)
    log += "\nsorted_horizontal_objects : "
    for i in objects:
        log += "\n" + str(i)
    log += "\n"
    objects = algorithm.post_processing(objects)
    objects = algorithm.arrange(objects)
    objects = algorithm.labeled2aksara(objects)
    objects = algorithm.unpackaksara(objects)
    objects = algorithm.aksara2latin2(objects)

    returnData = {
        "FILENAME" : filename,
        "TEXT" : objects,
        "AUDIO" : "-"
    }
    log += "\n" + str(returnData) + "\n"

    helper.send_telegram(f"===== SIARA =====\n aksara2latin \n {request.url_root}")
    helper.send_telegram_photo(resized_filepath)
    helper.send_telegram_photo(labeled_filepath)
    helper.send_telegram(log)

    os.remove(filepath)
    os.remove(resized_filepath)
    os.remove(labeled_filepath)
    log = ""

    return helper.composeReply("SUCCESS", "Hasil konversi gambar ke teks latin", returnData)


if __name__ == '__main__':
    runHost = "0.0.0.0"
    runDebug = True
    runPort = 5000
    app.run(host = runHost, port = runPort, debug = runDebug)
