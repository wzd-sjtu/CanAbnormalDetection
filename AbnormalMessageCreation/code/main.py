from AbnormalCreateClass import AttackCreate
from LoadDataClass import LoadDataClass
if __name__ == '__main__':
    path1 = "../src/testData/0.csv"
    path2 = "../src/testData/1.csv"
    loadDataExample = LoadDataClass()

    # loadDataExample.loadDataSnippet(path1, path2)
    # 制造攻击的速度并不需要特别的块，差不多就行了
    # 还有这个攻击的详细描述报告该怎样写呢？暂时是不清楚的

    loadDataExample.readOriginData()
    print(loadDataExample.sourceDataSnippet.iloc[0])

    attackCreateExample = AttackCreate()
    # 完成数据的初始导入
    attackCreateExample.sourceDataSnippet = loadDataExample.sourceDataSnippet
    attackCreateExample.historyNormalDataSnippet = loadDataExample.historyNormalDataSnippet

    # def insert_attack(self, id, normal_T, ratio, exist_time):
    # 是否真实完成了注入攻击呢？这里可能需要耦合
    # 为什么只存储了一个值呢？难以理解，一定是有一部分的算法出问题了
    # 我真的是直接裂开了

    attackCreateExample.insert_attack("82", 0.001, 2, 2)

