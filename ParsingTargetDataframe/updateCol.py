import pandas as pd

df_total = None
for i in range(1, 5):
    prefix = './src/'
    file_name = "test" + str(i) + ".csv"

    path = prefix + file_name
    if i == 1:
        df_total = pd.read_csv(path, index_col = 0)
    else:
        df_tmp = pd.read_csv(path, index_col = 0)
        df_total = df_total.append(df_tmp)
df_total.to_csv("./src/tmp_res2.csv")