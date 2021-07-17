# 记录正常数据的类
class SingleData:
    """每个SingleData实例化对象代表数据集的一行"""
    def __init__(self, number, can_id, time, length):
        self.number = number
        self.id = can_id
        self.time = time
        self.length = length


# 记录待检测数据的类
class SingleDataDetect:
    def __init__(self, number, can_id, time, length, ano):
        self.number = number
        self.id = can_id
        self.time = time
        self.length = length
        self.anomaly = ano


# 正常模型
class NormalSeqFeatures:
    """每个NormalSeqFeatures的实例化对象代表一个数据集的若干正常特征"""
    def __init__(self, stat, sr, cor):
        self.stat = stat    # 基本统计特征, {id: [numbers, avg_interval, min, max], ...}
        self.SR = sr        # 生存率阈值, {id : [min SR, max SR], ...}
        self.correlation = cor   # 余弦相似度, [cosSim of chunk 1, cosSim of chunk 2, ...]
