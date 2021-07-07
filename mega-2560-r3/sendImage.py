import serial
import time
import cv2
import numpy as np
import requests
import datetime
import json
import random

IMAGE_PATH = "https://cdn.discordapp.com/avatars/681531347583631444/fce74ef7998336e2d5ac7fa79c815674.png?size=4096"
IMAGE_IS_URL = True
DISPLAY_MAX_SIZE = [320, 240]
INTERPOLATION = cv2.INTER_AREA
GET_RANDOM_IMAGE = False
UNSPLASH_API_KEY = json.load(open("../api-key.json"))[0]

arduino = serial.Serial(port='/dev/ttyACM0', baudrate=1152000*2, timeout=0.001)

img = None
if GET_RANDOM_IMAGE:
    tmp = requests.get(f"https://api.unsplash.com/photos/random?client_id={UNSPLASH_API_KEY}&query=nature&orientation=landscape").json()
    url = tmp["urls"]["raw"]
    resp = requests.get(url, stream=True).raw
    img = np.asarray(bytearray(resp.read()), dtype="uint8")
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    print(f"""Writing image
Description: {tmp['description']}
Alt Description: {tmp['alt_description']}
URL: {tmp['links']['html']}
Attribution: A photo by {tmp['user']['name']}, taken in {tmp['location']['name'] or tmp['location']['title']}""")
elif IMAGE_IS_URL and not GET_RANDOM_IMAGE:
    resp = requests.get(IMAGE_PATH, stream=True).raw
    img = np.asarray(bytearray(resp.read()), dtype="uint8")
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
else:
    img = cv2.imread(IMAGE_PATH)
    print(f"Writing {IMAGE_PATH}")

rows, cols, channels = img.shape 

if cols > DISPLAY_MAX_SIZE[0] or rows > DISPLAY_MAX_SIZE[1]:
    if cols > rows:
        img = cv2.resize(img, (DISPLAY_MAX_SIZE[0], int(rows*(DISPLAY_MAX_SIZE[0]/cols))), interpolation=INTERPOLATION)
    else:
        img = cv2.resize(img, (int(cols*(DISPLAY_MAX_SIZE[1]/rows)), DISPLAY_MAX_SIZE[1]), interpolation=INTERPOLATION)

rows, cols, channels = img.shape

tmpixels = []
pixels = []

for y in range(rows):
    for x in range(cols):
        tmpixels.append(img[y,x])

def splitToBytes(color):
    return [
        (color & 0xff00) >> 8,
        color & 0x00ff
    ]

def gen565(r, g, b):
    return ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | (r >> 3)

def splitToBytes(color):
    return [
        (color & 0xff00) >> 8,
        color & 0x00ff
    ]

def writeColor(c):
    arduino.write(c)
    #time.sleep(.05)
    #d = arduino.read_all()
    #data = int(d.decode('utf-8'))
    #return hex(data)

for color in tmpixels:
    c = gen565(*color)
    tmp = splitToBytes(c)
    tmp.reverse()
    pixels.append(tmp)

start = time.time()

while arduino.in_waiting <= 0: 
    pass
arduino.write(bytes(str(cols), 'utf-8'))
arduino.readlines()

while arduino.in_waiting <= 0: 
    pass
arduino.write(bytes(str(rows), 'utf-8'))
arduino.readlines()

while len(pixels) > 0:
    while arduino.in_waiting <= 0: 
        pass
    #print("sent")
    toSend = int.from_bytes(arduino.read(), 'big')
    for i in range(toSend):
        try: color = pixels.pop(0)
        except: color = [0, 0]
        #print(writeColor(*color))
        writeColor(color)
    #print("sent")
        
end = time.time()

print(f"Time taken: {datetime.timedelta(seconds=end-start)}")

arduino.close()
