from selenium import webdriver

driver = webdriver.Firefox()
# driver.get('http://0422094080:Nahid_1212@sharepoint.pishgaman.net/')
driver.get('https://dyrk.org/tools/imei/')
print(driver.title)



'''import datetime

date_array = []
for i in range(0, 7):
    date_array.append(str(datetime.datetime.now().date() - datetime.timedelta(i)))

for item in date_array:
    print(item)'''