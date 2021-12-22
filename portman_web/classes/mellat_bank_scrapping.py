from io import BytesIO
# import cv2
from selenium import webdriver
from selenium.webdriver.common.by import By
from pytesseract import image_to_string
from PIL import Image, ImageEnhance, ImageFilter


def get_captcha():
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    driver.get('https://www.bpmellat.ir/portal')
    print(driver.title)
    driver.find_element(By.ID, 'username').send_keys("c602262")
    driver.find_element(By.ID, 'password').send_keys("10860123665")

    element = driver.find_element(By.XPATH,
                                  '//*[@id="wrap"]/div[4]/div/div/div/div/div/div[4]/div/form/captcha/div/div/div/ng-form/div/div/img')  # find part of the page you want image of
    location = element.location
    size = element.size
    png = driver.get_screenshot_as_png()  # saves screenshot of entire page
    driver.quit()

    im = Image.open(BytesIO(png))  # uses PIL library to open image in memory

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    im = im.crop((left, top, right, bottom))  # defines crop points
    im.save('/home/sajad/Project/portmanv3/portman_web/classes/screenshot.png')  # saves new cropped image

    # img = cv2.imread("/home/sajad/Project/portmanv3/portman_web/classes/screenshot.png")
    # gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # (h, w) = gry.shape[:2]
    # gry = cv2.resize(gry, (w * 2, h * 2))
    # cls = cv2.morphologyEx(gry, cv2.MORPH_CLOSE, None)
    # thr = cv2.threshold(cls, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # txt = image_to_string(thr)
    # print(txt)

# text = pytesseract.image_to_string(Image.open('screenshot.png'))
# print(text)

if __name__ == '__main__':
    print(get_captcha())
