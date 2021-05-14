import os
import random
import pandas as pd
import numpy as np

from BasicClass import SingleData,\
    DataList, DataListType, Rule, RuleMap
from CodingTypeChange import hex_str_to_binary_str, \
    binary_str_to_hex_str
from AbnormalDescriptionClass import AbnormalDescriptionClass

class AttackCreate:
    # 这个类里面有一些复杂的元素，暂时还没有完全实现的
    # 存储结构为dataframe结构，这一点是确定的
    # 元数据
    sourceDataSnippet = None
    # 各种重放攻击的来源源头
    historyNormalDataSnippet = None

    # 专门用于存储修改报文的information

    descriptionStruct = AbnormalDescriptionClass()
    # 由于这里是制造攻击，所以可以写的耦合起来
    # 正解
    ruleList = []
    myRuleMap = RuleMap()
    ruleLocation = "../src/learnedRule/result.csv"

    # dataframe字段？
    # time, can_id, data_in_binary, data_in_hex
    # 两个dataframe表格，这两个表格专门用于存储攻击信息，内容是固定的，是否有别的信息要加上去呢？

    # beforeChangedData = pd.DataFrame({"time":"","can_id":"","data_in_binary":"", "data_in_hex":""})
    beforeChangedData = pd.DataFrame(columns = ['time', 'can_id', 'data_in_binary', 'data_in_hex'])
    # afterChangedData = pd.DataFrame({"time":"","can_id":"","data_in_binary":"", "data_in_hex":""})
    afterChangedData = pd.DataFrame(columns = ['time', 'can_id', 'data_in_binary', 'data_in_hex'])
    # empty = empty.append(new, ignore_index=True)​ 这个是最终的递增方法，是确定的

    # 专门用于存放目标地址信息
    store_place = "../src/attack_test"


    def __init__(self):
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
        # 这几者之间的距离并不好确定
        loc_tmp = round(begin_time)
        begin_time = self.sourceDataSnippet.iloc[loc_tmp]['time']
        begin_time = begin_time + random.random()*(self.sourceDataSnippet.iloc[loc_tmp + 1]['time'] - begin_time)

        # 减小局部编码量
        tmp_origin_data = self.sourceDataSnippet

        # 下面是核心的insert的代码
        abnorma_T = normal_T/ratio
        end_time = exist_time + begin_time

        # 数据实际上一直在变化？
        for i in range(1, self.sourceDataSnippet.shape[0]-1):
            # 进行按行访问
            # 这样设计存在冲突后，程序异常退出的可能性possibility
            if begin_time > tmp_origin_data.iloc[i]['time'] and begin_time < tmp_origin_data.iloc[i + 1]['time']:


                # 至此完成了对应的注入攻击  选择将某一个报文标记为
                df1 = tmp_origin_data.iloc[:i+1]
                df2 = tmp_origin_data.iloc[i+1:]

                df3 = tmp_origin_data.iloc[i]
                df3 = df3.copy()
                # print(df3['can_id'])

                # data字段来自于别的地方，这样是合理的吗
                df3['time'] = begin_time
                # 在这里df的数据字段并没有进行复杂的修改
                df3['can_id'] = id
                df3['anormal'] = 1 # 证明是注入数据类型
                # 这里是注入攻击
                descriptionTmp = "insert attack!"

                # def updateBasicInformation(self, type, id, time, description, data_in_binary):
                self.descriptionStruct.updateBasicInformation(1, df3['can_id'],
                                                              df3['time'],
                                                              descriptionTmp,
                                                              df3['data_in_binary'])

                tmp_origin_data = (df1.append(df3)).append(df2)
                # print(len(tmp_origin_data))
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

        self.descriptionStruct.writeIntoCsv()

    # 删除攻击，在某一个时间段，去掉某个id的所有报文
    def erase_attack(self, id, exist_time):
        # 删除攻击的手段还是比较easy的，可以以较快的速度完成删除攻击
        document_name = "erase_attack_test.csv"
        # 在这里需要设定一系列参数的
        begin_time = random.random()
        # 这里标记的是begin的行
        begin_time = self.sourceDataSnippet.shape[0] * (2 / 3) * begin_time
        loc_tmp = round(begin_time)
        begin_time = self.sourceDataSnippet.iloc[loc_tmp]['time']

        # 减小局部编码量
        tmp_origin_data = self.sourceDataSnippet
        end_time = exist_time + begin_time

        for i in range(0, self.sourceDataSnippet.shape[0]):
            # 进行按行访问
            if self.sourceDataSnippet.iloc[i]['time'] >= begin_time and  self.sourceDataSnippet.iloc[i]['time'] <= end_time:

                id_name = tmp_origin_data.iloc[i]['can_id']
                if id_name == id:
                    df1 = tmp_origin_data.iloc[:i]
                    df2 = tmp_origin_data[i + 1:]

                    df3 = tmp_origin_data.iloc[i]
                    # 这里是删除攻击
                    descriptionTmp = "erase attack erase packet id is " + df3['can_id']
                    # 2代表删除攻击
                    # def updateBasicInformation(self, type, id, time, description, data_in_binary):
                    self.descriptionStruct.updateBasicInformation(2, df3['can_id'],
                                                                  df3['time'],
                                                                  descriptionTmp,
                                                                  df3['data_in_binary'])
                    tmp_origin_data = df1.append(df2)

        self.store_place = "../src/attack_test"
        document_name = document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)

        tmp_origin_data.to_csv(self.store_place + "/" + document_name)
        # 错误日志输出函数
        self.descriptionStruct.writeIntoCsv()
    # 重放攻击，把前一个时间段的数据重放到现在，可以指定id，也可以不指定全部重放？太明显了
    # 指定id重放 SingleId
    # 指定全体数据重放 AllData


    def reput_attack_SingleId(self, id, exist_time):
        # 报文id就是想要重放的id序列信息
        document_name = "reput_attack_SingleId_test.csv"

        # 重放在0.2s内的数据
        # exist_time = 0.5 # 重放在0.5s内的所有数据
        # 要重放，就要把所有的数据直接全体重放，这里的logic是固定的
        # 只会重放固定的数据的

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
        # copy是为了防止更改原始数据
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
                    # 不妨使用带索引数据
                    # 在这里使用索引修改数据

                    tmp_origin_data[i,'data_in_hex'] = reput_packet_data_in_hex[list_loc]
                    tmp_origin_data[i, 'data_in_binary'] = reput_packet_data_in_binary[list_loc]
                    tmp_origin_data[i, 'anormal'] = 3
                    df3 = tmp_origin_data.iloc[i]
                    descriptionTmp = "This data is reput, can you find it? There is no more information"
                    self.descriptionStruct.updateBasicInformation(3, df3['can_id'],
                                                                  df3['time'],
                                                                  descriptionTmp,
                                                                  df3['data_in_binary'])
                    # 直接修改元数据，注意进场时机！
                    list_loc = list_loc + 1

        self.store_place = "../src/attack_test"
        document_name = document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)

        tmp_origin_data.to_csv(self.store_place + "/" + document_name)
        self.descriptionStruct.writeIntoCsv()
        return None

    def reput_attack_AllData(self, exist_time):
        # 报文id就是想要重放的id序列信息

        # 问题本质是切片是否能修改的问题，现在的首要问题是加载数据格式不正确的问题

        document_name = "reput_attack_AllData_test.csv"

        # 这里reputList是全体想要reput的数据
        reputList = None
        begin_time = random.random()
        # 这里标记的是begin的行
        begin_time = self.historyNormalDataSnippet.shape[0] * (2 / 3) * begin_time
        begin_time = self.historyNormalDataSnippet.iloc[round(begin_time)]['time']
        tmp_origin_data = self.historyNormalDataSnippet

        end_time = exist_time + begin_time

        pre_begin_state = 0
        pre_end_state = 0
        pre_begin_loc_of_data = 0
        pre_end_loc_of_data = 0

        for i in range(0, self.historyNormalDataSnippet.shape[0]):
            # 进行按行访问
            if tmp_origin_data.iloc[i]['time'] >= begin_time and tmp_origin_data.iloc[i]['time'] <= end_time:
                # 存储我们目标的所有行
                if pre_begin_state == 0:
                    pre_begin_loc_of_data = i
                    pre_begin_state = 1
                else:
                    continue
            elif tmp_origin_data.iloc[i]['time'] >= end_time:
                if pre_end_state == 0:
                    # 实际上，这里的end_loc是开区间
                    pre_end_loc_of_data = i
                    pre_end_state = 1
                else:
                    continue
            else:
                continue

        # 直接进行数据切片即可
        reputList = tmp_origin_data.iloc[begin_loc_of_data:end_loc_of_data].copy()
        # print(reputList)

        # 下面处理重放的目标元数据
        # 记得完成标记操作哦
        begin_time = random.random()
        # 这里标记的是begin的行
        begin_time = self.sourceDataSnippet.shape[0] * (1 / 3) * begin_time
        begin_time = self.sourceDataSnippet.iloc[round(begin_time)]['time']
        # copy是为了防止更改原始数据
        tmp_origin_data = self.sourceDataSnippet.copy()
        # tmp_origin_data = tmp_origin_data.copy()
        end_time = exist_time + begin_time

        list_loc = 0

        # 在这里状态变量variables忘记归零了
        begin_state = 0
        end_state = 0
        begin_loc_of_data = 0
        end_loc_of_data = 0

        for i in range(0, self.sourceDataSnippet.shape[0]):
            if tmp_origin_data.iloc[i]['time'] >= begin_time and tmp_origin_data.iloc[i]['time'] <= end_time:
                # 存储我们目标的所有行
                if begin_state == 0:
                    begin_loc_of_data = i
                    begin_state = 1
                else:
                    continue
            else:
                continue
        end_loc_of_data = begin_loc_of_data + reputList.shape[0]
        all_len = tmp_origin_data.shape[0]
        df1 = tmp_origin_data[0:begin_loc_of_data]
        df2 = tmp_origin_data[end_loc_of_data:all_len]
        df3List = tmp_origin_data[begin_loc_of_data:end_loc_of_data]
        # 实际上，还是做时间区间映射是比较好的，直接用全体数据完全重放，不知道会有什么后果？

        # 这里不可以使用索引，数据表大幅度修改
        time_basic = df3List.iloc[0]['time']
        diff_basic_minus = reputList.iloc[0]['time'] - time_basic

        reputList.reset_index(inplace=True, drop=True)
        # print(diff_basic_minus)
        for reput_all_data_loc in range(0, reputList.shape[0]):
            # 直接时间填入，显然会造成时间割裂？
            reputList.iloc[[reput_all_data_loc]]['anormal'] = 4
            reputList.iloc[[reput_all_data_loc]]['time'] = reputList.iloc[[reput_all_data_loc]]['time'] - diff_basic_minus


            df3 = reputList.iloc[reput_all_data_loc]
            descriptionTmp = "This data is reput, can you find it? There is no more information"
            self.descriptionStruct.updateBasicInformation(4, df3['can_id'],
                                                          df3['time'],
                                                          descriptionTmp,
                                                          df3['data_in_binary'])

        tmp_origin_data = (df1.append(reputList)).append(df2)

        self.store_place = "../src/attack_test"
        document_name = document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)

        tmp_origin_data.to_csv(self.store_place + "/" + document_name)
        self.descriptionStruct.writeIntoCsv()
        return None


    def get_rule(self, doc_path):
        dfRule = pd.read_csv(self.ruleLocation)


        for row in dfRule.iterrows():
            # print(row[1]['can_id'])
            singleRule = Rule()
            # init_single_rule(self, can_id, begin_loc, end_loc, length, type_of_class, range)
            singleRule.init_single_rule(row[1]['can_id'], row[1]['begin_loc'], str(int(row[1]['begin_loc']) + int(row[1]['length']) - 1),
                                        row[1]['length'], row[1]['type'], row[1]['value_list'])
            self.myRuleMap.insertRule(singleRule)
        # self.myRuleMap.showAllRules() 暂时不要show了，对了就不要show了
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
    # 其实数据域修改并没有完善，还是有很多问题的
    def change_data_field(self, binary_str):
        return binary_str

