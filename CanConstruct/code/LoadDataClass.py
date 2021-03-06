# 本类用于统一构建输入的数据格式
import os
import random
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

# 这里免去把所有的功能写在一起，造成无法预知的后果。
class LoadDataClass:
    # 这里统一规定load的数据格式，算是一种去耦合的方式
    sourceDataSnippet = None
    historyNormalDataSnippet = None
    def __init__(self):
        return None
    def loadDataSnippet(self, path1, path2):
        # do_nothing
        self.sourceDataSnippet = pd.read_csv(path1, index_col=0)
        self.historyNormalDataSnippet = pd.read_csv(path2, index_col=0)
    def readOriginData(self):
        # 直接从源读取数据，需要适当修改一下的
        self.sourceDataSnippet = pd.read_csv("../src/webOriginData/test1.csv", index_col=0)
        self.historyNormalDataSnippet = pd.read_csv("../src/webOriginData/test2.csv", index_col=0)
                                                    # usecols=[0, 1, 2, 12, 13, 14, 15, 16])
    # 至此完成简单的数据初始化
    def readHadCutData(self):
        doc1Num = round(random.random()*175)
        doc2Num = round(random.random()*175)
        # 居然直接出错了？
        self.sourceDataSnippet = pd.read_csv("../src/HadCutData/" + str(doc1Num) + ".csv", index_col=0)
        self.historyNormalDataSnippet = pd.read_csv("../src/HadCutData/" + str(doc2Num) + ".csv", index_col=0)
        self.sourceDataSnippet = self.sourceDataSnippet.reset_index(drop=True)
        self.historyNormalDataSnippet = self.historyNormalDataSnippet.reset_index(drop=True)
