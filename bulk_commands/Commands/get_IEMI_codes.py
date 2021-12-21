from selenium import webdriver

driver = webdriver.Chrome()
# driver.get('http://0422094080:Nahid_1212@sharepoint.pishgaman.net/')
driver.get('https://www.bpmellat.ir/portal/#/')
print(driver.title)



'''import datetime

date_array = []
for i in range(0, 7):
    date_array.append(str(datetime.datetime.now().date() - datetime.timedelta(i)))

for item in date_array:
    print(item)'''