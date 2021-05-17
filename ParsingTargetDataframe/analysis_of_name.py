
import pandas as pd

df1 = pd.read_csv('result.csv')
print(df1)

dict_1 = {}
for i in range(0, int(df1.shape[0])):
    if df1.iloc[i]['can_id'] in dict_1:
        continue
    dict_1[df1.iloc[i]['can_id']] = 0
list = []
for item in dict_1:
    list.append(item)
print(list)