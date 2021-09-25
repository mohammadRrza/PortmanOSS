import os
import csv

directory = '/home/mrtbadboy/Desktop/CSV/New folder/'
total_directory = '/opt/total/'
total_file = open(total_directory + 'total.csv', 'w')
writer = csv.writer(total_file)
i = 1
for filename in os.listdir(directory):
    print('==================================')
    print(str(i) + "-" + filename)
    print('===================================')
    file_text = open(directory + filename, "r")
    for row in csv.reader(file_text):
        if 'CALLER_ID' not in row[0]:
            print(row)
            writer.writerow(row)
    i = i+1
    file_text.close()
print(i)
"""main_file = total_directory + 'total.csv'
read_file = open(main_file, 'r')
print(read_file.read())"""



