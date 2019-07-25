import pandas as pd, numpy as np
from datetime import datetime, time
from os import listdir
data_path = 'data/'
columns = ['Plnt', 'Material', 'Purch.Doc.', 'Item','OUn', 'Scheduled Qty', 'Deliv. Date']
months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
# months = ["JAN"]
monthly_frames=[]

def read_data(data_path, file):
    file_name = data_path + file
    datasheet = pd.read_csv(file_name, sep="\t", dtype = str, low_memory = False, usecols = columns)
    return datasheet
   


frames = [read_data(data_path, file_name) for file_name in listdir(data_path)]

result = pd.concat(frames)
result['KeyPurchdocItem'] = result['Purch.Doc.'].str[-9:] + result['Item']
print(result['Deliv. Date'].str[:2])
print(result)
for month in months:
    month_number = months.index(month)+1
    monthly_frames.append(result.loc[result['Deliv. Date'].str[:2] == month_number])

print(len(monthly_frames))
print(monthly_frames[1])


# for month in months:
#     start = datetime.now()
#     result[month + " Volumes"] = result.apply(lambda x: x['Scheduled Qty'] if months.index(month) + 1 == int(x['Deliv. Date'][:2]) else 0, axis = 1)
#     time_elapsed = datetime.now() - start
#     print("Done " + month + " in " + str(time_elapsed.seconds)  + " seconds")
# print(result)

