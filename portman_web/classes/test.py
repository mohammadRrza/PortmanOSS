import re
import sys
from datetime import datetime, timedelta
from io import BytesIO
import cv2
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pytesseract import image_to_string
from PIL import Image


def farzanegan_scrapping(username, password, owner_username):
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    chrome_options = Options()
    options.add_argument('--remote-debugging-port=9222')

    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=options)
    driver.get('https://ddr.farzaneganpars.ir:8443/wenex/loginpage.rose')
    print(driver.title)

    element = driver.find_element(By.XPATH, '//*[@id="captcha_img"]')  # find part of the page you want image of
    location = element.location
    size = element.size
    png = driver.get_screenshot_as_png()  # saves screenshot of entire page
    # driver.quit()

    im = Image.open(BytesIO(png))  # uses PIL library to open image in memory

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    im = im.crop((left, top, right, bottom))  # defines crop points
    im.save("/opt/portmanv3/portman_web/classes/far_captcha.png")  # saves new cropped image

    img = cv2.imread("/opt/portmanv3/portman_web/classes/far_captcha.png")
    gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (h, w) = gry.shape[:2]
    gry = cv2.resize(gry, (w * 2, h * 2))
    cls = cv2.morphologyEx(gry, cv2.MORPH_CLOSE, None)
    thr = cv2.threshold(cls, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    txt = image_to_string(img)
    print(txt)

if __name__ == "__main__":
    print('start')
    farzanegan_scrapping('Afra', '65465132', 'bitstream-afraertebat')
