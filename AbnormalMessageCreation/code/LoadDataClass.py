# 本类用于统一构建输入的数据格式
import os
import random
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

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
    # 至此完成简单的数据初始化

