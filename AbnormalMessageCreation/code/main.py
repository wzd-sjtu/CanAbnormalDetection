from AbnormalCreateClass import AttackCreate
from LoadDataClass import LoadDataClass
if __name__ == '__main__':
    path1 = "../src/testData/0.csv"
    path2 = "../src/testData/1.csv"
    loadDataExample = LoadDataClass()

    loadDataExample.loadDataSnippet(path1, path2)

    attackCreateExample = AttackCreate()
    # 完成数据的初始导入
    attackCreateExample.sourceDataSnippet = loadDataExample.sourceDataSnippet
    attackCreateExample.historyNormalDataSnippet = loadDataExample.historyNormalDataSnippet

    # def insert_attack(self, id, normal_T, ratio, exist_time):
    # 是否真实完成了注入攻击呢？这里可能需要耦合
    attackCreateExample.insert_attack("C9", 0.01, 3, 2)

