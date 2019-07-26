from datetime import datetime
from os import listdir
import pandas as pd

DATA_PATH = 'data/'
COLUMNS = ['Plnt', 'Material', 'Purch.Doc.', 'Item', 'OUn', 'Scheduled Qty', 'Deliv. Date']
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

MONTH_NUMBERS = ['0' + str(i) if i < 10 else str(i) for i in range(1, 13)]
print(MONTH_NUMBERS)
# MONTHS = ["JAN"]
monthly_frames = []

def read_data(data_path, file):
    file_name = data_path + file
    datasheet = pd.read_csv(file_name, sep="\t", dtype=str, low_memory=False, usecols=COLUMNS)
    return datasheet
   

frames = [read_data(DATA_PATH, file_name) for file_name in listdir(DATA_PATH)]

result = pd.concat(frames)


# result['KeyPurchdocItem'] = result['Purch.Doc.'].str[-9:] + result['Item']

result.reset_index(drop=True, inplace=True)

start = datetime.now()
result.sort_values(by='Deliv. Date', inplace=True)

for month in MONTH_NUMBERS:
    monthly_frames.append(result.loc[result['Deliv. Date'].str[:2] == month])
    monthly_frames[MONTH_NUMBERS.index(month)][MONTHS[MONTH_NUMBERS.index(month)] + " Volumes"] = pd.to_numeric(monthly_frames[MONTH_NUMBERS.index(month)]['Scheduled Qty'])
    print("Done " + MONTHS[MONTH_NUMBERS.index(month)])

# for month in MONTH_NUMBERS:
#     print(monthly_frames[MONTH_NUMBERS.index(month)])

result = pd.concat(monthly_frames, sort=False).fillna(0)
time_elapsed = datetime.now() - start
print("Done in " + str(time_elapsed.seconds)  + " seconds")
# print(result)
print(result.dtypes)

grouped = result.groupby(['Purch.Doc.', "Item", 'Plnt', 'Material', 'OUn']).agg(dict.fromkeys((month + " Volumes" for month in MONTHS), 'sum'))

# result.astype({'Scheduled Qty': 'float64'}, copy=False).dtypes

print(grouped)
'''
Avg time for this section is 12 * ~17 seconds
for month in MONTHS:
    start = datetime.now()
    result[month + " Volumes"] = result.apply(lambda x: x['Scheduled Qty'] if MONTHS.index(month) + 1 == int(x['Deliv. Date'][:2]) else 0, axis = 1)
    time_elapsed = datetime.now() - start
    print("Done " + month + " in " + str(time_elapsed.seconds)  + " seconds")
print(result)
'''
