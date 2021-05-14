from AbnormalCreateClass import AttackCreate
from LoadDataClass import LoadDataClass
from BasicClass import DataFieldAttackInformation

if __name__ == '__main__':
    path1 = "../src/testData/0.csv"
    path2 = "../src/testData/1.csv"
    loadDataExample = LoadDataClass()

    # loadDataExample.loadDataSnippet(path1, path2)
    # 制造攻击的速度并不需要特别的块，差不多就行了
    # 还有这个攻击的详细描述报告该怎样写呢？暂时是不清楚的

    # 从location直接获取数据即可
    loadDataExample.readOriginData()
    # print(loadDataExample.sourceDataSnippet.iloc[0])

    attackCreateExample = AttackCreate()
    # 完成数据的初始导入
    # 数据的初始解码有问题的？我直接裂开了
    attackCreateExample.sourceDataSnippet = loadDataExample.sourceDataSnippet
    attackCreateExample.historyNormalDataSnippet = loadDataExample.historyNormalDataSnippet

    # def insert_attack(self, id, normal_T, ratio, exist_time)
    # attackCreateExample.insert_attack('82', 0.01, 2,0.2)
    # def erase_attack(self, id, exist_time):
    # attackCreateExample.erase_attack('82', 0.2)
    # def reput_attack_SingleId(self, id, exist_time):
    # attackCreateExample.reput_attack_SingleId("82", 0.2)
    # 这种全体reput貌似需要一小段时间？为了时间对齐！
    # attackCreateExample.reput_attack_AllData(0.1)
    # attackCreateExample.changedatafield_attack_randomly('82', 0.2)

    #

    # attackCreateExample.changedatafield_attack_const_or_multivalue('565', 0.2)
    # attackCreateExample.get_rule(" ")

    valueAttackInfo = DataFieldAttackInformation()
    valueAttackInfo.attackChoseType = valueAttackInfo.sensorAttack
    valueAttackInfo.relatedThing = valueAttackInfo.max_value_attack
    attackCreateExample.change_data_field(valueAttackInfo, '82', 0.02)


