from selenium import webdriver

driver = webdriver.Firefox()
driver.get('https://dyrk.org/tools/imei/')
print(driver.title)
f = open("/opt/portmanv3/bulk_commands/Commands/IEMI_Codes.txt", "w")
for x in range(1, 5000):
    driver.find_element_by_xpath('/html/body/input[1]').click()
    IEMI_code = driver.find_element_by_id('imei_num')
    IEMI_code_value = IEMI_code.get_attribute('value')
    f.write(IEMI_code_value+'\n')
f.close()


'''import datetime

date_array = []
for i in range(0, 7):
    date_array.append(str(datetime.datetime.now().date() - datetime.timedelta(i)))

for item in date_array:
    print(item)'''