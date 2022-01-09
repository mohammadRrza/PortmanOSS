import re
from io import BytesIO
import cv2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from pytesseract import image_to_string
from PIL import Image, ImageEnhance, ImageFilter


def get_captcha():
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
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
    im.save('/home/sajad/Project/portmanv3/portman_web/classes/far_captcha.png')  # saves new cropped image

    img = cv2.imread("/home/sajad/Project/portmanv3/portman_web/classes/far_captcha.png")
    gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (h, w) = gry.shape[:2]
    gry = cv2.resize(gry, (w * 2, h * 2))
    cls = cv2.morphologyEx(gry, cv2.MORPH_CLOSE, None)
    thr = cv2.threshold(cls, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    txt = image_to_string(thr)
    print(txt)

    driver.find_element(By.ID, 'j_username_visible').send_keys("Pishgaman3")
    driver.find_element(By.ID, 'j_password').send_keys("123456")
    driver.find_element(By.ID, 'captcha_input').send_keys(txt)
    # ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
    # WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions).until(
    #     expected_conditions.presence_of_element_located((By.ID, 'login_btn_submit')))
    try:
        driver.find_element(By.ID, 'login_btn_submit').click()
    except StaleElementReferenceException as Exception:
        driver.find_element(By.XPATH, '//*[@id="accordionItemId_div"]/div[1]/a').click()
        driver.get('https://ddr.farzaneganpars.ir:8443/wenex/ddr/list.rose?sessionid=6582FC29BECA5E5F6B80ED83891E8769')
        provider_name = driver.find_element(By.XPATH, '//*[@id="ddrList"]/tbody/tr/td[1]').text
        print(provider_name)
        total_traffic_gb = driver.find_element(By.XPATH, '//*[@id="ddrList"]/tbody/tr/td[2]').text
        print(total_traffic_gb)
        used_traffic_gb = driver.find_element(By.XPATH, '//*[@id="ddrList"]/tbody/tr/td[3]').text
        print(used_traffic_gb)
        remain_traffic_gb = driver.find_element(By.XPATH, '//*[@id="ddrList"]/tbody/tr/td[4]').text
        print(remain_traffic_gb)
        total_numbers = driver.find_element(By.XPATH, '//*[@id="ddrList"]/tbody/tr/td[5]').text
        print(total_numbers)
        used_numbers = driver.find_element(By.XPATH, '//*[@id="ddrList"]/tbody/tr/td[6]').text
        print(used_numbers)
        remain_numbers = driver.find_element(By.XPATH, '//*[@id="ddrList"]/tbody/tr/td[7]').text
        print(remain_numbers)
        total_data_volume = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/table/tbody/tr[2]/td').text
        total_data_volume = re.findall(r'(?:Total Data Volume)[a-zA-Z\s\(\):]+\d*,\d*\.*\d*', total_data_volume)[0]
        print(total_data_volume)
        total_records_number = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/table/tbody/tr[2]/td/span[1]').text
        print(total_records_number)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    get_captcha()
