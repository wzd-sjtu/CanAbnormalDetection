import matplotlib.pyplot as plt
import pandas as pd

name_list = []
for i in range(0, 176):
    name_list.append(str(i))

num_list = []

for i in range(0, 176):
    file_name = "../src/HadCutData/" + str(i) + ".csv"
    df1 = pd.read_csv(file_name)
    unique_num = len(list(df1['can_id'].unique()))
    num_list.append(unique_num)

for item in num_list:
    if item != 44:
        print("happy!")



