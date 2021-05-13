import pandas as pd

df = pd.read_csv("../src/webOriginData/test_res.csv")
df = (df[df['subnet'] == 4])
df.to_csv("only_for_test_output.csv")