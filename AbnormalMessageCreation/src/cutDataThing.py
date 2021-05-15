import pandas as pd

# 会自动生成对应的索引
df1 = pd.read_csv('target_res.csv', index_col=0)

lenofDf = df1.shape[0]

begin_loc = 0
end_loc = 0
begin_time = df1.iloc[0]['time']
print(begin_time)
# print(type(begin_time)) 发现是float

times_of_doc = 0

# 等前一个算法跑完，现在有点跑不动的
# 这个算法还是比较easy的
for i in range(0, lenofDf):
    if df1.iloc[i]['time'] - begin_time >= 3:
        end_loc = i
        dfTmp = df1.iloc[begin_loc:end_loc].copy()
        begin_loc = i # 发现这个数据在3s界限内
        dfTmp.to_csv('./HadCutData/' + str(times_of_doc) + ".csv")
        times_of_doc = times_of_doc + 1
        begin_time = df1.iloc[i]['time']
    else:
        continue
