import os
import random
import pandas as pd
import numpy as np

from BasicClass import SingleData,\
    DataList, DataListType, Rule
from CodingTypeChange import hex_str_to_binary_str, \
    binary_str_to_hex_str


class AttackCreate:
    # 这个类里面有一些复杂的元素，暂时还没有完全实现的
    # 存储结构为dataframe结构，这一点是确定的
    # 元数据
    sourceDataSnippet = None
    # 各种重放攻击的来源源头
    historyNormalDataSnippet = None

    ruleList = []
    # dataframe字段？
    # time, can_id, data_in_binary, data_in_hex
    # 两个dataframe表格，这两个表格是没有意义的
    # beforeChangedData = pd.DataFrame({"time":"","can_id":"","data_in_binary":"", "data_in_hex":""})
    beforeChangedData = pd.DataFrame(columns = ['time', 'can_id', 'data_in_binary', 'data_in_hex'])
    # afterChangedData = pd.DataFrame({"time":"","can_id":"","data_in_binary":"", "data_in_hex":""})
    afterChangedData = pd.DataFrame(columns = ['time', 'can_id', 'data_in_binary', 'data_in_hex'])
    # empty = empty.append(new, ignore_index=True)​ 这个是最终的递增方法，是确定的
    store_place = "../src/attack_test"

    def renewChangeInformation(self, pre, next):
        self.beforeChangedData = self.beforeChangedData.append(pre, ignore_index = True)
        self.afterChangedData = self.afterChangedData.append(next, ignore_index=True)
    # 两个函数，专门为了重放攻击开发的
    def renewChangeInformationPre(self, pre):
        self.beforeChangedData = self.beforeChangedData.append(pre, ignore_index=True)
    def renewChangeInformationNext(self, next):
        self.afterChangedData = self.afterChangedData.append(next, ignore_index=True)

    def __init__(self):
        # 原本的类是没有必要放进去的，直接用新的类即可
        self.origin_place = None
        self.target_place = None
        self.store_place = None

        self.origin_data = None
        self.target_data = None
        self.store_data = None

        self.origin_data_num = 0
        self.target_data_num = 0

        # 这里命名有点过于随意了
        self.input_num = None
        self.source_num = None
    # 这个是填充数据类的内容
    def load_data(self):
        # 这里的数据来自上传的源数据，需要以后再慢慢考虑的
        # 使用简单的手段制造攻击
        return None
    # DataList
    # 不同的attack有不同的精度参数，也就是说这里的列表白给了？

    def create_attack(self):
        return None

    # 注入攻击，在某个时间段，注入某一个id的报文，数据字段可靠性不保证
    def insert_attack(self, id, normal_T, ratio, exist_time):
        # 参数意义注解
        # id 报文id
        # normal_T 经过序列分析，得知这个报文的周期
        # ratio 注入周期是报文周期的倍数
        # exist_time 注入报文攻击的持续时间

        # 在这里需要进行注入攻击
        # 这种攻击输出的文件名字前缀
        document_name = "insert_attack_test.csv"

        begin_time = random.random()
        # 这里的origindata存的是dataframe，我真是醉了
        begin_time = self.sourceDataSnippet.shape[0]*(2/3)*begin_time
        begin_time = self.sourceDataSnippet.iloc[round(begin_time)]['time']

        # 减小局部编码量
        tmp_origin_data = self.sourceDataSnippet

        # 下面是核心的insert的代码
        abnorma_T = normal_T/ratio
        end_time = exist_time + begin_time

        for i in range(1, self.sourceDataSnippet.shape[0]-1):
            # 进行按行访问
            if begin_time >= tmp_origin_data.iloc[i]['time'] and begin_time <= tmp_origin_data.iloc[i]['time']:


                # 至此完成了对应的注入攻击  选择将某一个报文标记为
                df1 = tmp_origin_data.iloc[:i+1]
                df2 = tmp_origin_data.iloc[i+1:]

                df3 = tmp_origin_data.iloc[i]
                df3 = df3.copy()

                df3['time'] = begin_time
                df3['can_id'] = id

                # 这里是注入攻击
                self.renewChangeInformation(df3, df3)

                tmp_origin_data = (df1.append(df3)).append(df2)
                # print(tmp_origin_data.shape[0])

                begin_time = begin_time + abnorma_T
                if begin_time + abnorma_T >= end_time:
                    break

        # 攻击报文存储
        self.store_place = "../src/attack_test"
        document_name = document_name + str(begin_time) + "_" + str(self.input_num)+".csv"
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)

        tmp_origin_data.to_csv(self.store_place + "/" + document_name)

        # 记得这里要把所有数据都导入
        self.beforeChangedData.to_csv(self.store_place + "/" + "before_" + document_name)
        self.afterChangedData.to_csv(self.store_place + "/" + "after_" + document_name)
        # 最好加一个异常或者正常标志位，这个要求稍微有点高的。

    # 删除攻击，在某一个时间段，去掉某个id的所有报文
    def erase_attack(self, id, exist_time):
        document_name = "erase_attack_test.csv"
        # 在这里需要设定一系列参数的
        begin_time = random.random()
        # 这里标记的是begin的行
        begin_time = self.sourceDataSnippet.shape[0] * (2 / 3) * begin_time
        begin_time = self.sourceDataSnippet.iloc[round(begin_time)]['time']

        # 减小局部编码量
        tmp_origin_data = self.sourceDataSnippet
        end_time = exist_time + begin_time

        for i in range(0, self.origin_data.shape[0]):
            # 进行按行访问
            if self.sourceDataSnippet.iloc[i]['time'] >= begin_time and  self.sourceDataSnippet.iloc[i]['time'] <= end_time:

                id_name = tmp_origin_data.iloc[i]['can_id']
                if id_name == id:
                    df1 = tmp_origin_data.iloc[:i]
                    df2 = tmp_origin_data[i + 1:]

                    # 这里是删除攻击
                    self.renewChangeInformation(tmp_origin_data.iloc[i], tmp_origin_data.iloc[i])
                    tmp_origin_data = df1.append(df2)

        self.store_place = "../src/attack_test"
        document_name = document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)

        tmp_origin_data.to_csv(self.store_place + "/" + document_name)

    # 重放攻击，把前一个时间段的数据重放到现在，可以指定id，也可以不指定全部重放？太明显了
    # 显然，这里重放的是数据字段，这一点是需要考虑的
    def reput_attack(self, id, exist_time):
        # 报文id就是想要重放的id序列信息
        document_name = "reput_attack_test.csv"
        # 在这里需要设定一系列参数的
        # exist_time = 0.5 # 重放在0.5s内的所有数据
        reput_packet_data_in_hex = []
        reput_packet_data_in_binary = []
        # 从源数据中提取重放数据
        begin_time = random.random()
        # 这里标记的是begin的行
        begin_time = self.historyNormalDataSnippet.shape[0] * (2 / 3) * begin_time
        begin_time = self.historyNormalDataSnippet.iloc[round(begin_time)]['time']
        tmp_origin_data = self.historyNormalDataSnippet

        end_time = exist_time + begin_time

        for i in range(0, self.historyNormalDataSnippet.shape[0]):
            # 进行按行访问
            if tmp_origin_data.iloc[i]['time'] >= begin_time and tmp_origin_data.iloc[i]['time'] <= end_time:

                if tmp_origin_data.iloc[i]['can_id'] == id:
                    reput_packet_data_in_hex.append(tmp_origin_data.iloc[i]['data_in_hex'])
                    reput_packet_data_in_binary.append(tmp_origin_data.iloc[i]['data_in_binary'])
                # print(tmp_origin_data.shape[0])

        # 下面处理重放的目标元数据
        begin_time = random.random()
        # 这里标记的是begin的行
        begin_time = self.sourceDataSnippet.shape[0] * (2 / 3) * begin_time
        begin_time = self.sourceDataSnippet.iloc[round(begin_time)]['time']

        # 减小局部编码量
        tmp_origin_data = self.sourceDataSnippet.copy()
        # tmp_origin_data = tmp_origin_data.copy()
        end_time = exist_time + begin_time


        list_loc = 0
        for i in range(0, self.sourceDataSnippet.shape[0]):
            # 进行按行访问
            if tmp_origin_data.iloc[i]['time'] >= begin_time and tmp_origin_data.iloc[i]['time'] <= end_time:
                if tmp_origin_data.iloc[i]['can_id'] == id and list_loc < len(reput_packet_data_in_hex):
                    # tmp_origin_data.iloc[i]['data_in_hex'] = reput_packet_data_in_hex[list_loc]
                    # tmp_origin_data.iloc[i]['data_in_binary'] = reput_packet_data_in_binary[list_loc]

                    tmp_origin_data.iloc[i, 3] = reput_packet_data_in_hex[list_loc]
                    tmp_origin_data.iloc[i, 2] = reput_packet_data_in_binary[list_loc]

                    list_loc = list_loc + 1

        self.store_place = "../src/attack_test"
        document_name = document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)

        tmp_origin_data.to_csv(self.store_place + "/" + document_name)
        return None

    def get_rule(self, doc_path):
        # 从目标文件中读取规则文件，为某些操作打下了基础
        tmp = Rule()
        # 最后的range使用的应当是字符串？
        tmp.init_single_rule(0, 64, 0, [125])
        # 在这里一共有几个类呢？

        self.ruleList.append(tmp)
        return None

    # 数据域字段修改攻击，假设得到了某些邪恶的规则字段
    def changedatafield_attack(self, id, doc_path, attackType, exist_time):
        # 这种数据域攻击主要有两种：
        # 一种是使用将某个字段设置为最大or最小常量
        # 另一种是历史序列重放，可以认为是变种重返攻击
        self.get_rule(doc_path)

        '''
        const_tag = 0
        multi_value_tag = 1
        sensor_or_counter_tag = 2

        counter_tag = 2
        sensor_tag = 3
        no_meaning_tag = 4

        攻击的mod：
        const_attack: yes or no
        multi_value_atack: 统一修改为第i个数值，这里i的生成方式可以固定，也可以随机
        counter_attack: +1 +2 +3 修改数值即可
        sensor_attack: max-value, min-value, any-value
        '''
        # 这里是统一的文件输入位置，可以考虑加一个函数load
        document_name = "changedatafield_attack_test.csv"
        # 在这里需要设定一系列参数的
        # exist_time = 0.5  # 修改在0.5s内的所有数据


        # 从源数据中提取重放数据
        begin_time = random.random()
        # 这里标记的是begin的行
        begin_time = self.historyNormalDataSnippet.shape[0] * (2 / 3) * begin_time
        begin_time = self.historyNormalDataSnippet.iloc[round(begin_time)]['time']
        tmp_origin_data = self.historyNormalDataSnippet

        end_time = exist_time + begin_time


        for i in range(0, self.origin_data.shape[0]):
            # 进行按行访问
            if tmp_origin_data.iloc[i]['time'] >= begin_time and tmp_origin_data.iloc[i]['time'] <= end_time:
                if tmp_origin_data.iloc[i]['can_id'] == id:
                    tmp_str = tmp_origin_data.iloc[i]['data_in_binary']
                    # 这里显然是不太舒服的，我真的是直接裂开了
                    res_str = self.change_data_field(tmp_str, attackType) # 进行了某种级别的攻击，这里需要先定义接口，再进行不同种类的攻击书写
                    tmp_origin_data.iloc[i, 2] = res_str
                    tmp_origin_data.iloc[i, 2] = binary_str_to_hex_str(res_str)

        # 下面的存储操作是完全类似的，是可以封装为函数的部分
        self.store_place = "../src/attack_test"
        document_name = document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)
        tmp_origin_data.to_csv(self.store_place + "/" + document_name)
        return None

    # 整个程序的粒度还是不太够，代码的耦合性还是有点过强了
    # 以后在debug中，可能会遇上无法计算的bug
    # 发现这里修改的是二进制数据？64位二进制
    def change_data_field(self, binary_str):
        return binary_str

