import cv2
import pytesseract
from io import BytesIO
import requests
import numpy as np


def remove_noise(image):
    return cv2.medianBlur(image, 5)


pytesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = pytesseract_path

c = 'https://media.discordapp.net/attachments/707486957206372385/708513822310137916/unknown.png'
response = BytesIO(requests.get(c).content)
i = cv2.imdecode(np.asarray(bytearray(response.read()), dtype="uint8"), cv2.IMREAD_COLOR)
hsv = cv2.cvtColor(i, cv2.COLOR_BGR2HSV)
hsv_channels = cv2.split(hsv)

rows = i.shape[0]
cols = i.shape[1]

for i in range(0, rows):
    for j in range(0, cols):
        h = hsv_channels[0][i][j]
        s = hsv_channels[1][i][j]

        if 20 < h < 35 and s > 230:
            hsv_channels[2][i][j] = 0
        else:
            hsv_channels[2][i][j] = 255

# cv2.imshow("test", hsv_channels[2])
cv2.waitKey(0)

print(pytesseract.image_to_string(hsv_channels[2]))
