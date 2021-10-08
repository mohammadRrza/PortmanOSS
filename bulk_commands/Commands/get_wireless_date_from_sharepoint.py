import time

from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome('chromedriver')
driver.get('http://0422094080:Nahid_1212@sharepoint.pishgaman.net/')
driver.get('http://sharepoint.pishgaman.net/SE/BW/Lists/BandwidthSubscribers/EditForm.aspx?ID=3034&Source=http%3A%2F%2Fsharepoint%2Epishgaman%2Enet%2FSE%2FBW%2FSitePages%2FBWAll%2Easpx')
time.sleep(5)
s = driver.find_element_by_id('lbl_NationalID')
print(s.text)
driver.close()
"""for i in range(1, 101):
    print('************************************************************')
    for j in range(14, 60):
        rows = driver.find_element_by_xpath("/html/body/form/div[12]/div/div[3]/div/div[1]/div[2]/div[4]/div[4]/div/div/table/tbody/tr/td/div/div/div/div[1]/div/div/div/table/tbody/tr/td/table/tbody[2]/tr[1]")
        print('========================================')
        print(str(i)+"-"+str(j)+"-"+row.text)
        print('========================================')
    print('************************************************************')"""

