import os
import random
import pandas as pd
import numpy as np

from BasicClass import SingleData,\
    DataList, DataListType, Rule, RuleMap
from CodingTypeChange import hex_str_to_binary_str, \
    binary_str_to_hex_str
from AbnormalDescriptionClass import AbnormalDescriptionClass

# 写代码结构化有利于自己写的更清晰
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

    # 需要每一次生成的文件名字都相同，存在覆盖原理
    document_name = "attack_data.csv"
    def refresh_place(self):
        self.store_place = "../src/attack_test"
        self.ruleLocation = "../src/learnedRule/result.csv"

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

        self.refresh_place()

        self.document_name = "attack_data.csv"

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
                descriptionTmp = "This message is an insert attaction!"

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
        # 我裂开，这些文件路径都要进行修改，真的醉了
        # 统一异常报文数据？对的
        document_name = self.document_name
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)
        tmp_origin_data.to_csv(self.store_place + "/" + document_name)

        self.descriptionStruct.writeIntoCsv()

    # 删除攻击，在某一个时间段，去掉某个id的所有报文
    def erase_attack(self, id, exist_time):
        # 删除攻击的手段还是比较easy的，可以以较快的速度完成删除攻击
        # document_name = "erase_attack_test.csv" 不需要再声明了
        # 在这里需要设定一系列参数的
        self.refresh_place()

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
                    descriptionTmp = "can id is " + df3['can_id'] +" It is erased!"
                    # 2代表删除攻击
                    # def updateBasicInformation(self, type, id, time, description, data_in_binary):
                    self.descriptionStruct.updateBasicInformation(2, df3['can_id'],
                                                                  df3['time'],
                                                                  descriptionTmp,
                                                                  df3['data_in_binary'])
                    tmp_origin_data = df1.append(df2)

        # document_name = document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"
        document_name = self.document_name
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
        # document_name = "reput_attack_SingleId_test.csv"

        # 重放在0.2s内的数据
        # exist_time = 0.5 # 重放在0.5s内的所有数据
        # 要重放，就要把所有的数据直接全体重放，这里的logic是固定的
        # 只会重放固定的数据的
        self.refresh_place()

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
        # print(list_loc)

        for i in range(0, self.sourceDataSnippet.shape[0]):
            # 进行按行访问
            if tmp_origin_data.iloc[i]['time'] >= begin_time and tmp_origin_data.iloc[i]['time'] <= end_time:
                if tmp_origin_data.iloc[i]['can_id'] == id and list_loc < len(reput_packet_data_in_hex):

                    descriptionTmp = "id is " + id + " pre data is " + tmp_origin_data.iloc[i]['data_in_hex']

                    tmp_origin_data.loc[i,'data_in_hex'] = reput_packet_data_in_hex[list_loc]
                    tmp_origin_data.loc[i, 'data_in_binary'] = reput_packet_data_in_binary[list_loc]
                    tmp_origin_data.loc[i, 'anormal'] = 3
                    df3 = tmp_origin_data.iloc[i]

                    descriptionTmp = descriptionTmp + " now data is " + tmp_origin_data.iloc[i]['data_in_hex']
                    self.descriptionStruct.updateBasicInformation(3, df3['can_id'],
                                                                  df3['time'],
                                                                  descriptionTmp,
                                                                  df3['data_in_binary'])
                    # 直接修改元数据，注意进场时机！
                    list_loc = list_loc + 1

        # document_name = self.document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"

        # 文件存储的逻辑logic
        document_name = self.document_name
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)

        tmp_origin_data.to_csv(self.store_place + "/" + document_name)
        self.descriptionStruct.writeIntoCsv()
        return None

    def reput_attack_AllData(self, exist_time):
        # 报文id就是想要重放的id序列信息

        # 问题本质是切片是否能修改的问题，现在的首要问题是加载数据格式不正确的问题

        # document_name = "reput_attack_AllData_test.csv"

        # 这里reputList是全体想要reput的数据
        reputList = None
        begin_time = random.random()

        self.refresh_place()

        # 这里标记的是begin的行
        begin_time = self.historyNormalDataSnippet.shape[0] * (2 / 3) * begin_time
        begin_time = self.historyNormalDataSnippet.iloc[round(begin_time)]['time']
        tmp_origin_data = self.historyNormalDataSnippet

        end_time = exist_time + begin_time

        pre_begin_state = 0
        pre_end_state = 0
        pre_begin_loc_of_data = 0
        pre_end_loc_of_data = 0

        # 这里的重放是一大块直接重放？
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



        # 下面处理重放的目标元数据
        # 记得完成标记操作哦
        begin_time = random.random()
        # 这里标记的是begin的行
        begin_time = self.sourceDataSnippet.shape[0] * (1 / 3) * begin_time
        begin_time = self.sourceDataSnippet.iloc[round(begin_time)]['time']
        # copy是为了防止更改原始数据

        # copy就是把数据完成了复制的过程
        tmp_origin_data = self.sourceDataSnippet
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
        end_loc_of_data = begin_loc_of_data + pre_end_loc_of_data - pre_begin_loc_of_data
        # 找到结尾坐标就是最好的解决方式

        tmp_origin_data = self.historyNormalDataSnippet.copy() # 直接copy所有数据，切片是无法赋值的
        tmp_origin_data_next = self.sourceDataSnippet

        time_diff = tmp_origin_data.iloc[pre_begin_loc_of_data]['time'] - tmp_origin_data_next.iloc[begin_loc_of_data]['time']
        print(time_diff)

        length_of_reput = pre_begin_loc_of_data - begin_loc_of_data

        for love in range(pre_begin_loc_of_data, pre_end_loc_of_data):
            # 这个才是dataframe的最终精髓
            # 只能用loc进行索引定位？iloc返回的总是切片
            tmp_origin_data.loc[love, 'time'] = tmp_origin_data.iloc[love]['time'] - time_diff
            tmp_origin_data.loc[love, 'anormal'] = 4

            # 在这里就记得记录存在小问题的信息
            df3 = tmp_origin_data.iloc[love]
            # 把这里的数据要存储回去的？
            descriptionTmp = "this data is the reput data"
            self.descriptionStruct.updateBasicInformation(4, df3['can_id'],
                                                          df3['time'],
                                                          descriptionTmp,
                                                          df3['data_in_binary'])

            loc1 = love - length_of_reput

            df3 = tmp_origin_data_next.iloc[loc1]
            descriptionTmp = "this data is the origin data"
            self.descriptionStruct.updateBasicInformation(4, df3['can_id'],
                                                          df3['time'],
                                                          descriptionTmp,
                                                          df3['data_in_binary'])

        df1 = tmp_origin_data_next.iloc[0:begin_loc_of_data]
        df2 = tmp_origin_data_next[end_loc_of_data:tmp_origin_data_next.shape[0]]
        df3 = tmp_origin_data.iloc[pre_begin_loc_of_data:pre_end_loc_of_data]

        tmp_origin_data = (df1.append(df3)).append(df2)
        # tmp_origin_data.to_csv("test.csv")
        # document_name = document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"
        # 最后数据统一存储即可
        document_name = self.document_name
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)

        tmp_origin_data.to_csv(self.store_place + "/" + document_name)
        self.descriptionStruct.writeIntoCsv()

        return None

    # 以上的所有代码都不涉及复杂的修改

    # get_rule 是已经测试过的函数
    # 首先要给出一个规则的展示表格？用什么实现呢？暂时是未知的

    def get_rule(self, doc_path):
        dfRule = pd.read_csv(self.ruleLocation)
        self.refresh_place()

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
    # 这里是经典的数据域修改攻击，这里的索引是what situation呢？
    # 暂时不太清楚数据域修改攻击应当如何实现呢？

    # 数据域攻击的修改是博大精深的，可以做的简单一点，也可以做的复杂一些
    # 以下这个函数暂时先废弃
    def changedatafield_attack(self, id, attackType, exist_time):
        # 这种数据域攻击主要有两种：
        # 一种是使用将某个字段设置为最大or最小常量
        # 另一种是历史序列重放，可以认为是变种重返攻击
        # doc path是完全不需要的
        # 只对某种报文进行数据域修改，description也是暂时不需要的，应该是的吧
        self.refresh_place()

        self.get_rule(" ")

        '''
        新的tag标志
        
        checksum_tag = 0
        sensor_tag = 1
        const_tag = 2
        counter_tag = 3
        multi_value_tag = 4
        no_meaning_tag = 5
        
        攻击的mod：
        以下的mod如何决定呢？暂时是不清楚的哦
        const_attack: yes or no
        multi_value_atack: 统一修改为第i个数值，这里i的生成方式可以固定，也可以随机
        counter_attack: +1 +2 +3 修改数值即可
        sensor_attack: max-value, min-value, any-value
        '''
        # 这里是统一的文件输入位置，可以考虑加一个函数load
        # document_name = "changedatafield_attack_test.csv"
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
        # document_name = document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"
        document_name = self.document_name
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)
        tmp_origin_data.to_csv(self.store_place + "/" + document_name)
        return None

    # 这个是进行完全随机修改的实现函数，难度还是ok的
    def changedatafield_attack_randomly(self, id, exist_time):
        # attackType就是 case switch的根本决定因素
        self.get_rule(" ")
        self.refresh_place()
        # document_name = "changedatafield_attack_test.csv"

        # 从源数据中提取重放数据
        begin_time = random.random()
        begin_time = self.sourceDataSnippet.shape[0] * (2 / 3) * begin_time
        begin_time = self.sourceDataSnippet.iloc[round(begin_time)]['time']
        tmp_origin_data = self.sourceDataSnippet
        end_time = exist_time + begin_time

        for i in range(0, self.sourceDataSnippet.shape[0]):
            if tmp_origin_data.iloc[i]['time'] >= begin_time and tmp_origin_data.iloc[i]['time'] <= end_time \
                    and tmp_origin_data.iloc[i]['can_id'] == id:
                # 正式进入random环节
                # 从前半部分直接random到后半部分
                random_begin_bit = round(random.random()*32)
                length_of_bit = round(random.random()*32)
                random_end_bit = random_begin_bit + length_of_bit - 1

                target_binary_bit = tmp_origin_data.iloc[i]['data_in_binary']
                descriptionTmp = "before binary is " + target_binary_bit[random_begin_bit:random_end_bit+1]

                target_binary_bit = list(target_binary_bit)
                for love in range(random_begin_bit, random_end_bit+1):
                    if(random.random()>0.5): target_binary_bit[love] = '0'
                    else: target_binary_bit[love] = '1'

                target_binary_bit = "".join(target_binary_bit)
                descriptionTmp = descriptionTmp + " end binary is " + target_binary_bit[random_begin_bit:random_end_bit+1]
                tmp_origin_data.loc[i, 'data_in_binary'] = target_binary_bit
                tmp_origin_data.loc[i, 'data_in_hex'] = binary_str_to_hex_str(target_binary_bit)
                tmp_origin_data.loc[i, 'anormal'] = 5
                hex_data = binary_str_to_hex_str(target_binary_bit)
                for peace in range(0, 8):
                    tmp_origin_data.loc[i, 'data' + str(peace)] = hex_data[2*peace:2*peace+2]

                df3 = tmp_origin_data.iloc[i]

                self.descriptionStruct.updateBasicInformation(5, df3['can_id'],
                                                              df3['time'],
                                                              descriptionTmp,
                                                              df3['data_in_binary'])

        # document_name = document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"
        document_name = self.document_name
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)
        tmp_origin_data.to_csv(self.store_place + "/" + document_name)
        self.descriptionStruct.writeIntoCsv()

    # 我直接裂开，测试不了emm
    def changedatafield_attack_const_or_multivalue(self, id, exist_time):
        # 这二者的名字是一样的？但是攻击类型是否需要相同呢？暂时是未知的
        self.get_rule(" ")
        self.refresh_place()
        # document_name = "changedatafield_attack_test.csv"
        # 从源数据中提取重放数据
        begin_time = random.random()
        begin_time = self.sourceDataSnippet.shape[0] * (2 / 3) * begin_time
        begin_time = self.sourceDataSnippet.iloc[round(begin_time)]['time']
        tmp_origin_data = self.sourceDataSnippet
        end_time = exist_time + begin_time

        # 首先得到目标列表，存放的是Rule Class的类
        tmp_rule_list = self.myRuleMap.getTargetCanIdRule(id)
        final_rule_list = []
        for item in tmp_rule_list:
            if item.type_of_class == 2 or item.type_of_class == 4:
                final_rule_list.append(item)
        # 存储好我们接下来要操作的类即可，这种操作是某种程度 to some extent 合理的
        # 这里就随便选几个规则，都改一改

        for i in range(0, self.sourceDataSnippet.shape[0]):
            if tmp_origin_data.iloc[i]['time'] >= begin_time and tmp_origin_data.iloc[i]['time'] <= end_time \
                    and tmp_origin_data.iloc[i]['can_id'] == id:
                # 正式进入random环节
                # 从前半部分直接random到后半部分
                # print("successfully")

                random_num = round(random.random()*(len(final_rule_list)-1)) # 取到这个值即可

                ruleSingle = final_rule_list[random_num]

                random_begin_bit = ruleSingle.begin_loc
                length_of_bit = ruleSingle.length
                random_end_bit = ruleSingle.end_loc
                val_range = ruleSingle.range


                target_binary_bit = tmp_origin_data.iloc[i]['data_in_binary']
                descriptionTmp = ""
                if ruleSingle.type_of_class == 2:
                    descriptionTmp = descriptionTmp + "This is a const value: "
                else: # multi表示有很多个数值，处理过程是合理的
                    descriptionTmp = descriptionTmp + "This is a multi value: "

                descriptionTmp = "before binary is " + target_binary_bit[random_begin_bit:random_end_bit + 1]

                target_binary_bit = list(target_binary_bit)
                for love in range(random_begin_bit, random_end_bit + 1):
                    if (random.random() > 0.5):
                        target_binary_bit[love] = '0'
                    else:
                        target_binary_bit[love] = '1'

                target_binary_bit = "".join(target_binary_bit)
                descriptionTmp = descriptionTmp + " end binary is " + target_binary_bit[
                                                                      random_begin_bit:random_end_bit + 1]
                tmp_origin_data.loc[i, 'data_in_binary'] = target_binary_bit
                tmp_origin_data.loc[i, 'data_in_hex'] = binary_str_to_hex_str(target_binary_bit)
                tmp_origin_data.loc[i, 'anormal'] = 6
                hex_data = binary_str_to_hex_str(target_binary_bit)
                for peace in range(0, 8):
                    tmp_origin_data.loc[i, 'data' + str(peace)] = hex_data[2 * peace:2 * peace + 2]

                df3 = tmp_origin_data.iloc[i]

                self.descriptionStruct.updateBasicInformation(6, df3['can_id'],
                                                              df3['time'],
                                                              descriptionTmp,
                                                              df3['data_in_binary'])

        # document_name = document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"

        document_name = self.document_name
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)
        tmp_origin_data.to_csv(self.store_place + "/" + document_name)
        self.descriptionStruct.writeIntoCsv()

    # 这里basicType接口并没有完全定义？
    # 设置很多图片是否有意义呢？没有意义
    # 直接选择上下左右定位是比较好的
    def changedatafield_attack_sensro(self, id, exist_time, basicType):
        # 不知道传感器的攻击可以选择到什么粒度，也不知道究竟可以制造哪种类型的攻击呢？
        # 这几者都是暂时未知的
        # 实际上，sensor的修改尺度是由attackType决定的，这是一个复杂的攻击配置变量
        # 这二者的名字是一样的？但是攻击类型是否需要相同呢？暂时是未知的
        self.get_rule(" ")
        self.refresh_place()
        # document_name = "changedatafield_attack_test.csv"
        # 从源数据中提取重放数据
        begin_time = random.random()
        begin_time = self.sourceDataSnippet.shape[0] * (2 / 3) * begin_time
        begin_time = self.sourceDataSnippet.iloc[round(begin_time)]['time']
        tmp_origin_data = self.sourceDataSnippet
        end_time = exist_time + begin_time

        # 首先得到目标列表，存放的是Rule Class的类
        tmp_rule_list = self.myRuleMap.getTargetCanIdRule(id)
        final_rule_list = []
        for item in tmp_rule_list:
            if item.type_of_class == 1:
                final_rule_list.append(item)
        # 存储好我们接下来要操作的类即可，这种操作是某种程度 to some extent 合理的
        # 这里就随便选几个规则，都改一改
        if len(final_rule_list) == 0:
            # document_name = document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"
            document_name = self.document_name
            if not os.path.exists(self.store_place):
                os.mkdir(self.store_place)
            tmp_origin_data = tmp_origin_data.loc[0].copy()
            tmp_origin_data.to_csv(self.store_place + "/" + document_name)
            self.descriptionStruct.writeIntoCsv()
            return

        for i in range(0, self.sourceDataSnippet.shape[0]):
            if tmp_origin_data.iloc[i]['time'] >= begin_time and tmp_origin_data.iloc[i]['time'] <= end_time \
                    and tmp_origin_data.iloc[i]['can_id'] == id:
                # 正式进入random环节
                # 从前半部分直接random到后半部分

                random_num = round(random.random() * (len(final_rule_list) - 1))  # 取到这个值即可

                ruleSingle = final_rule_list[random_num]

                random_begin_bit = int(ruleSingle.begin_loc)
                length_of_bit = int(ruleSingle.length)
                random_end_bit = int(ruleSingle.end_loc)
                val_range = ruleSingle.range

                # 接下来对传感器的change是严格的，在某种程度上是严格的

                target_binary_bit = tmp_origin_data.iloc[i]['data_in_binary']
                descriptionTmp = "This is sensor value changing "

                # 这里居然使用的是硬编码，将来是很有可能出现问题的
                if basicType == 0:
                    descriptionTmp = descriptionTmp + " max-value change "
                elif basicType == 1:
                    descriptionTmp = descriptionTmp + " min-value change "
                elif basicType == 2:
                    descriptionTmp = descriptionTmp + " random-value change "
                elif basicType == 3:
                    descriptionTmp = descriptionTmp + " apt advanced change "

                descriptionTmp = descriptionTmp + " before binary is " + target_binary_bit[random_begin_bit:random_end_bit + 1]

                target_binary_bit = list(target_binary_bit)

                # 以下是攻击的核心内容，根据不同的type，制造不同类型的攻击
                # 想要实现多态攻击，这里的粒度还暂时不够
                if basicType == 2: # 不一定在传感器取值范围
                    for love in range(random_begin_bit, random_end_bit + 1):
                        if (random.random() > 0.5):
                            target_binary_bit[love] = '0'
                        else:
                            target_binary_bit[love] = '1'
                elif basicType == 0:
                    for love in range(random_begin_bit, random_end_bit + 1):
                        target_binary_bit[love] = '1'
                elif basicType == 1:
                    for love in range(random_begin_bit, random_end_bit + 1):
                        target_binary_bit[love] = '0'


                target_binary_bit = "".join(target_binary_bit)

                descriptionTmp = descriptionTmp + " end binary is " + target_binary_bit[
                                                                      random_begin_bit:random_end_bit + 1]
                tmp_origin_data.loc[i, 'data_in_binary'] = target_binary_bit
                tmp_origin_data.loc[i, 'data_in_hex'] = binary_str_to_hex_str(target_binary_bit)
                tmp_origin_data.loc[i, 'anormal'] = 7
                hex_data = binary_str_to_hex_str(target_binary_bit)
                for peace in range(0, 8):
                    tmp_origin_data.loc[i, 'data' + str(peace)] = hex_data[2 * peace:2 * peace + 2]

                df3 = tmp_origin_data.iloc[i]

                self.descriptionStruct.updateBasicInformation(7, df3['can_id'],
                                                              df3['time'],
                                                              descriptionTmp,
                                                              df3['data_in_binary'])

        # document_name = document_name + str(begin_time) + "_" + str(self.input_num) + ".csv"
        document_name = self.document_name
        if not os.path.exists(self.store_place):
            os.mkdir(self.store_place)
        tmp_origin_data.to_csv(self.store_place + "/" + document_name)
        self.descriptionStruct.writeIntoCsv()

        # 至此完成了各种类之间的耦合操作，还是合理的哦
        return

    # 到现在为止，一共造出了7种攻击，以及很多需要配置的参数
    # 需要单独开一个类，对攻击进行描述，提供可供选择的type哦

    # 别的修改方式和这里的随机修改，在整个大框架上绝对是相似的
    def change_data_field(self, attackBasicInformation, id, exist_time):
        # 这里的attackBasicInformation 专门用于分支循环调用
        self.refresh_place()
        if attackBasicInformation.attackChoseType == attackBasicInformation.randomAttack:
            self.changedatafield_attack_randomly(id, exist_time)
        elif attackBasicInformation.attackChoseType == attackBasicInformation.constOrMultivalueAttack:
            self.changedatafield_attack_const_or_multivalue(id, exist_time)
        elif attackBasicInformation.attackChoseType == attackBasicInformation.sensorAttack:
            self.changedatafield_attack_sensro(id, exist_time, attackBasicInformation.relatedThing)
        return

    # 至此，应当是完成了这个基本类的编写
    # 后面需要把这个数据结构部署到网页上去，从而为将来的展示打下较好的基础

    # 幸亏进行了类的封装，否则后期绝对会出问题

