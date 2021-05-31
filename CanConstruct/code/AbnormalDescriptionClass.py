import pandas as pd
import CodingTypeChange
from CodingTypeChange import binary_str_to_hex_str
# 这个类用于输出需要的异常信息
class AbnormalDescriptionClass:

    # 现在暂时先确定四种不同类型的攻击
    # 这里可能需要导入周期信息，从而提高可用性？
    # 0即为正常数据，这点注意
    # attackType使用字母+数字动态组合即可
    dataFrameList = pd.DataFrame(columns = ['time', 'can_id', 'attackType', 'description', 'data_in_binary', 'data_in_hex'])

    dictAttackStrToNum = {"insert attack":1, "erase attack":2, "reput attack":3, "changedatafield attack":4}
    dictNumToAttack = {1:"insert attack", 2:"erase attack", 3:"reput attack", 4:"changedatafield attack"}
    attackType = None
    attackCanId = None
    attackTime = None
    # 别的信息是不需要存储在这里的，这个信息总是恒定的
    # 攻击的具体内容，这个应当如何输出日志呢？暂时是不清楚的
    # 这种代码没有持久化操作，显然是不舒服的
    attackDescription = None # 典型的描述攻击的具体操作是什么，这个可以在制造攻击时动态写入，没有办法分割开来？
    attackData = None
    # 如何定义消息日志呢？这个是输出攻击具体消息的日志
    def updateBasicInformation(self, type, id, time, description, data_in_binary):
        # self.attackType = self.dictNumToAttack[type]
        self.attackType = type
        self.attackCanId = id
        self.attackTime = time
        self.attackDescription = description
        self.attackData = data_in_binary

        self.writeIntoInnerStruct()
        return
    def writeIntoInnerStruct(self):
        # 目标是返回一个dataframe，这个算是最重要的目标喽
        # description其实是需要添加的数据？
        dict_tmp = {}
        dict_tmp['time'] = self.attackTime
        dict_tmp['can_id'] = self.attackCanId
        dict_tmp['attackType'] = self.attackType
        dict_tmp['description'] = self.attackDescription
        dict_tmp['data_in_hex'] = binary_str_to_hex_str(self.attackData)
        dict_tmp['data_in_binary'] = self.attackData

        dataSmallFrame = pd.DataFrame([dict_tmp])
        self.dataFrameList = self.dataFrameList.append(dataSmallFrame)
        # 这里只是单纯的写出文件而已
    def writeIntoCsv(self):
        self.dataFrameList.to_csv('../src/attackDescription/myDescription.csv')
        self.dataFrameList = None
        # 当写完以后，记得置空，从而为内存空间打下基础
        self.dataFrameList = pd.DataFrame(columns=['time', 'can_id', 'attackType', 'description', 'data_in_binary', 'data_in_hex'])