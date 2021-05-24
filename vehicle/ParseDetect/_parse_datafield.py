
import pandas as pd
import numpy as np
import time
from .used_class import *

threshold_num = 96
grad_threshold = 36
high_threshold_num = 8
high_grad_threshold = 10
combine_likely_grad_threshold = 96


class ParseData:
    checksum_tag = 0
    sensor_tag = 1
    const_tag = 2
    counter_tag = 3
    multi_value_tag = 4
    no_meaning_tag = 5

    def __init__(self, dataframe):
        self.train_data_frame = dataframe
        self.train_data_frame.replace('0', '00', inplace=True)

        self.train_CANID_set = set(self.train_data_frame['can_id'])
        self.time = time.perf_counter()  # 记录代码执行时间
        self.sum_time = 0
        self.allCANID_sensor_dict = {}
        self.result_array = []

        # 生成dataframe用到的结构
        self.id_list = []
        self.type_list = []
        self.begin_loc_list = []
        self.length_list = []
        self.score_list = []
        self.value_store_list = []

        self.result_dict = {}
        self.result_dict['can_id'] = []
        self.result_dict['start_bit'] = []
        self.result_dict['end_bit'] = []
        self.result_dict['type'] = []
        self.result_dict['value_range'] = []

    def run_time(self, tag):  # 简单的记录时间函数
        new_time = time.perf_counter()
        print(tag, new_time - self.time)
        self.time = new_time

    def time_in(self):
        self.time = time.perf_counter()

    def time_out(self, tag):
        new_time = time.perf_counter()
        self.sum_time = new_time - self.time + self.sum_time

    def run(self):

        for can_id in self.train_CANID_set:
            self.can_id = can_id
            self.singID_train_data_frame = self.train_data_frame[self.train_data_frame['can_id'] == can_id]
            # self.run_time('create time: ')
            self.init_before_classify()
            # self.run_time('Init time: ')
            self.store_data_tostrbin()
            # self.run_time('toint time: ')
            if self.is_not_zero():
                self.find_checksum()
                # self.run_time('checksum time: ')
                self.find_sensor()
                self.find_high_sensor()
                # self.run_time('sensor time: ')
                self.inital_available_section()
                # self.run_time('Init_available time: ')
                self.initial_classfy_data()
                # self.run_time('Init_classify time: ')
                self.process_classfy_data()
                # self.run_time('process time: ')
                self.greedy_find_solution()
                # self.run_time('greedy time: ')

            else:
                self.save_zero_results()

            self.print_result()
            self.result_save()
        self.to_dataframe()
        self.run_time('total:time')
        print(self.sum_time)

    def init_before_classify(self):

        self.strbin_data_series = None  # 二进制字符串数据序列

        self.checksum_pos = None  # 校验和位置
        self.sensor_list = []  # 传感器位置list
        self.check_and_sensor_list = []

        self.byte_num = int(self.singID_train_data_frame.iat[0, 2])  # 字节数
        self.bit_length = self.byte_num * 8  # 比特数
        # classfy_results_list是分好类的数据
        self.classfy_results_list = []  # 保存结果矩阵

        # 用于存储每一轮迭代中每种类别的最优解
        self.const_class = None
        self.multi_value_class = None

        self.counter_class = None
        self.no_meaning_class = None

        self.sensor_res = []
        self.final_res = []
        self.available_set_section = set([])

    def store_data_tostrbin(self):

        data_array = self.singID_train_data_frame.iloc[:, 3].values
        for i in range(1, self.byte_num):
            data_array = data_array + self.singID_train_data_frame.iloc[:, i + 3].values
        self.strbin_data_series = pd.Series(data_array)

        self.strbin_data_series = self.strbin_data_series.apply(
            lambda x: ('{:064b}'.format(int(x, 16)))[64 - self.bit_length:64])
        # self.strbin_data_series = self.strbin_data_series.apply(lambda x: x)
        column_name = list(self.singID_train_data_frame.columns)
        del column_name[0:3]
        self.number_data_frame = pd.DataFrame(index=self.singID_train_data_frame.index, columns=column_name)

        for i in range(0, self.byte_num):
            self.number_data_frame.iloc[:, i] = self.singID_train_data_frame.iloc[:, i + 3].apply(lambda x: int(x, 16))

    def initial_classfy_data(self):
        for section in self.available_set_section:
            for i in range(section[0], section[1] + 1):
                for j in range(section[0], section[1] + section[0] + 1 - i):
                    tmp_classfy_data = Classfy_Results()
                    tmp_classfy_data.classfy_begin_loc = i
                    tmp_classfy_data.classfy_length = j - section[0] + 1
                    self.classfy_results_list.append(tmp_classfy_data)

    def find_checksum(self):

        # self.number_data_frame['sum'] = self.number_data_frame.apply(lambda x: x.sum() % 256,axis =1)
        self.number_data_frame['sum'] = self.number_data_frame.sum(axis=1) % 256

        for i in range(0, self.byte_num):
            # self.number_data_frame.loc[:,'bool'] = self.number_data_frame.apply(lambda x: x['sum'] == x['data' + str(i)] * 2 % 256,axis =1)
            a = (self.number_data_frame.loc[:, 'sum'] == self.number_data_frame.iloc[:, i].values * 2 % 256)
            if a.all():
                self.checksum_pos = i
                tmp_result = Classfy_Results()
                tmp_result.classfy_begin_loc = 8 * i
                tmp_result.classfy_length = 8
                tmp_result.classfy_class = self.checksum_tag
                tmp_result.classfy_score = self.number_data_frame.size
                self.final_res.append(tmp_result)

    def find_sensor(self):

        for i in range(0, self.byte_num):
            diverse_value_set = set(self.number_data_frame.iloc[:, i])
            if len(diverse_value_set) > threshold_num:
                if i != self.checksum_pos:
                    self.sensor_list.append(i)
                    grad = int(self.number_data_frame.iloc[:, i].diff().abs().max())
                    data_max = max(diverse_value_set)
                    data_min = min(diverse_value_set)
                    tmp_result = Classfy_Results()
                    tmp_result.classfy_begin_loc = 8 * i
                    tmp_result.classfy_length = 8
                    tmp_result.classfy_class = self.sensor_tag
                    tmp_result.classfy_value_store = [data_min, data_max, grad]
                    tmp_result.classfy_score = len(diverse_value_set)
                    self.sensor_res.append(tmp_result)

        self.check_and_sensor_list = self.sensor_list[:]
        if self.checksum_pos is not None:
            self.check_and_sensor_list.append(self.checksum_pos)

    def find_high_sensor(self):
        tmp_sensor_list = self.sensor_list[:]
        for i in tmp_sensor_list:
            if i > 0 and i - 1 not in self.check_and_sensor_list:
                if len(set(self.number_data_frame.iloc[:, i - 1])) >= high_threshold_num:
                    self.number_data_frame['diff'] = self.number_data_frame.iloc[:, i - 1].diff()
                    if (self.number_data_frame['diff'].abs().max() < high_grad_threshold):
                        self.number_data_frame['sum'] = self.number_data_frame.iloc[:,
                                                        i - 1] * 256 + self.number_data_frame.iloc[:, i]
                        self.number_data_frame['sumdiff'] = self.number_data_frame['sum'].diff()
                        likely = self.number_data_frame[
                            (self.number_data_frame['sumdiff'] <= combine_likely_grad_threshold) & (
                                        self.number_data_frame['diff'] != 0)].shape[0]
                        unlikely = self.number_data_frame[self.number_data_frame['diff'] != 0].shape[0] - likely
                        if likely > unlikely:
                            for tmp_res in self.sensor_res:
                                if tmp_res.classfy_begin_loc == 8 * i:
                                    self.sensor_res.remove(tmp_res)
                                    break
                            grad = int(self.number_data_frame['sumdiff'].abs().max())
                            data_max = self.number_data_frame['sum'].max()
                            data_min = self.number_data_frame['sum'].min()
                            tmp_result = Classfy_Results()
                            tmp_result.classfy_begin_loc = 8 * (i - 1)
                            tmp_result.classfy_length = 16
                            tmp_result.classfy_class = self.sensor_tag
                            tmp_result.classfy_value_store = [data_min, data_max, grad]
                            tmp_result.classfy_score = len(set(self.number_data_frame['sum']))
                            self.final_res.append(tmp_result)
                            if self.can_id not in self.allCANID_sensor_dict:
                                self.allCANID_sensor_dict[self.can_id] = []
                            self.allCANID_sensor_dict[self.can_id].append('data' + str(i - 1) + str(i))
                            self.sensor_list.remove(i)
                            self.check_and_sensor_list.append(i - 1)

                            continue

        self.final_res = self.final_res + self.sensor_res
        if self.can_id not in self.allCANID_sensor_dict:
            self.allCANID_sensor_dict[self.can_id] = []
        for i in self.sensor_list:
            self.allCANID_sensor_dict[self.can_id].append('data' + str(i))

    def is_counter(self, sec_data_list, length, begin_loc):
        if length not in [2, 4, 6, 8] or begin_loc % 2 != 0:
            return 0
        sec_data_list = [int(x, 2) for x in sec_data_list]

        for i in range(1, len(sec_data_list)):
            if ((sec_data_list[i] - sec_data_list[i - 1]) % (2 ** length) != 1):
                return 0
        return 1

    def is_not_zero(self):
        p = self.number_data_frame.any(axis=None)
        return p

    def inital_available_section(self):
        self.available_set_section.add((0, self.bit_length - 1))

        for i in self.check_and_sensor_list:
            begin_loc = 8 * i
            end_loc = 8 * (i + 1) - 1
            for section in self.available_set_section:
                if section[1] < begin_loc:
                    continue
                elif section[0] > end_loc:
                    continue
                else:
                    target_loc = []
                    left_begin_loc = section[0]
                    left_end_loc = begin_loc - 1
                    right_begin_loc = end_loc + 1
                    right_end_loc = section[1]

                    if left_end_loc >= left_begin_loc:
                        target_loc.append((left_begin_loc, left_end_loc))
                    if right_end_loc >= right_begin_loc:
                        target_loc.append((right_begin_loc, right_end_loc))

                    self.available_set_section.remove((section[0], section[1]))
                    for item in target_loc:
                        self.available_set_section.add(item)
                    break

    def process_classfy_data(self):
        for classfy_result in self.classfy_results_list:

            diverse_value_set = set([])
            sec_data_list = []
            begin_loc = classfy_result.classfy_begin_loc
            end_loc = classfy_result.classfy_length + begin_loc - 1
            length = classfy_result.classfy_length

            # self.time_in()
            new_series = self.strbin_data_series.apply(lambda x: x[begin_loc: end_loc + 1])
            # self.time_out('time:')
            sec_data_list = new_series.tolist()
            diverse_value_set = set(sec_data_list)

            '''
            for data in self.data_series:
                sec_data = (data & sec_standard_data) >> (self.bit_length - end_loc - 1)
                diverse_value_set.add(sec_data)
                sec_data_list.append(sec_data)
            length = classfy_result.classfy_length
            '''
            # self.run_time('2 time: ')
            if len(diverse_value_set) == 1:
                # classfy_result.classfy_class = "const"
                classfy_result.classfy_class = self.const_tag
                classfy_result.classfy_score = length

                classfy_result.classfy_value_store = list(diverse_value_set)

            elif self.is_counter(sec_data_list, length, begin_loc):

                classfy_result.classfy_class = self.counter_tag
                classfy_result.classfy_score = length

                classfy_result.classfy_value_store = []

                '''

                elif is_sensor(self,data_sec_list):
                # classfy_result.classfy_class = "sensor or counter"
                # 以下是score的计算方法

                #
                # 在这里是传感器？
                classfy_result.classfy_class = self.sensor_tag
                classfy_result.classfy_score = (len(s) * len(s) / 2 ** length)

                classfy_result.classfy_value_store = []
                middle_no_use_list = []
                for str_binary_value in s:
                    middle_no_use_list.append(int(str_binary_value, 2))

                classfy_result.classfy_value_store.append(min(middle_no_use_list))
                classfy_result.classfy_value_store.append(max(middle_no_use_list))

                # classfy_result.classfy_score = (len(s) / 2 ** length)
                '''

            # elif len(s) <= min(2**(0.5*length), 12):
            elif len(diverse_value_set) <= min(2 ** (0.5 * length), 12) and length >= 3:
                # classfy_result.classfy_class = "multi-value"
                classfy_result.classfy_class = self.multi_value_tag
                classfy_result.classfy_score = length

                # classfy_result.classfy_value_type = 0
                classfy_result.classfy_value_store = list(diverse_value_set)

            else:
                classfy_result.classfy_class = self.no_meaning_tag
                classfy_result.classfy_score = length
                classfy_result.classfy_value_store = []
            # self.run_time('3 time: ')

    def greedy_find_solution(self):
        while len(self.available_set_section) != 0:
            for section in self.available_set_section:
                begin_loc = section[0]
                length = section[1] - section[0] + 1
                end_loc = section[1]

                for classfy_result in self.classfy_results_list:
                    if classfy_result.classfy_begin_loc >= begin_loc and \
                            classfy_result.classfy_length + classfy_result.classfy_begin_loc - 1 <= end_loc:
                        if classfy_result.classfy_class == self.const_tag:
                            if self.const_class is None:
                                self.const_class = classfy_result
                            else:
                                if self.const_class.classfy_score < classfy_result.classfy_score:
                                    self.const_class = classfy_result

                        elif classfy_result.classfy_class == self.counter_tag:
                            if self.counter_class is None:
                                self.counter_class = classfy_result
                            else:
                                if self.counter_class.classfy_score < classfy_result.classfy_score:
                                    self.counter_class = classfy_result

                        elif classfy_result.classfy_class == self.multi_value_tag:
                            if self.multi_value_class is None:
                                self.multi_value_class = classfy_result
                            else:
                                if self.multi_value_class.classfy_score < classfy_result.classfy_score:
                                    self.multi_value_class = classfy_result


                        elif classfy_result.classfy_class == self.no_meaning_tag:
                            if self.no_meaning_class is None:
                                self.no_meaning_class = classfy_result
                            else:
                                if self.no_meaning_class.classfy_score < classfy_result.classfy_score:
                                    self.no_meaning_class = classfy_result

            # 选择最优解的关键函数
            # tmp_res = choose_max(self.const_class, self.multi_value_class, self.sensor_counter_class, self.no_meaning_class)
            tmp_res = choose_max(self.const_class,
                                 self.counter_class,
                                 self.multi_value_class,
                                 self.no_meaning_class)
            self.final_res.append(tmp_res)
            if tmp_res is None:
                print(self.can_id)
            # print("i am happy:::  " + str(tmp_res.classfy_class))

            # 一轮迭代完成，需要进行归空操作
            self.const_class = None
            self.multi_value_class = None
            self.sensor_counter_class = None

            self.counter_class = None
            self.sensor_class = None
            self.no_meaning_class = None
            begin_loc = tmp_res.classfy_begin_loc
            l = tmp_res.classfy_length
            end_loc = begin_loc + l - 1

            # 可行区间更新
            target_loc = []
            target_b = None
            target_e = None

            for section in self.available_set_section:
                if section[1] < begin_loc:
                    continue
                elif section[0] > end_loc:
                    continue
                else:
                    left_begin_loc = section[0]
                    left_end_loc = begin_loc - 1
                    right_begin_loc = end_loc + 1
                    right_end_loc = section[1]

                    target_b = section[0]
                    target_e = section[1]

                    if left_end_loc >= left_begin_loc:
                        target_loc.append((left_begin_loc, left_end_loc))
                    if right_end_loc >= right_begin_loc:
                        target_loc.append((right_begin_loc, right_end_loc))
                    break

            if target_b is not None and target_e is not None:
                self.available_set_section.remove((target_b, target_e))
            for item in target_loc:
                self.available_set_section.add(item)
            # print("已经完成分类过程")

    def save_zero_results(self):

        tmp_classfy_data = Classfy_Results()
        tmp_classfy_data.classfy_begin_loc = 0
        tmp_classfy_data.classfy_length = self.bit_length
        tmp_classfy_data.classfy_score = self.bit_length
        tmp_classfy_data.classfy_class = self.const_tag
        tmp_classfy_data.classfy_value_store = [0]
        self.final_res.append(tmp_classfy_data)

    def print_result(self):
        print(self.can_id)
        for classfy_result in self.final_res:
            self.result_dict['can_id'].append(self.can_id)
            self.result_dict['start_bit'].append(classfy_result.classfy_begin_loc)
            self.result_dict['end_bit'].append(classfy_result.classfy_begin_loc + classfy_result.classfy_length - 1)
            self.result_dict['type'].append(classfy_result.classfy_class)
            self.result_dict['value_range'].append(classfy_result.classfy_value_store)

            print(str(classfy_result.classfy_begin_loc) + " " + \
                  str(classfy_result.classfy_begin_loc + classfy_result.classfy_length - 1) \
                  + " " + str(classfy_result.classfy_class) + " " + str(classfy_result.classfy_score) + " ")

    def result_save(self):

        for classfy_result in self.final_res:
            self.id_list.append(self.can_id)
            self.type_list.append(classfy_result.classfy_class)
            self.begin_loc_list.append(classfy_result.classfy_begin_loc)
            self.length_list.append(classfy_result.classfy_length)
            self.score_list.append(classfy_result.classfy_score)
            if classfy_result.classfy_class == 2 or classfy_result.classfy_class == 4:
                tmp_classfy_value_store = []
                for i in classfy_result.classfy_value_store:
                    if type(i) is not int:
                        tmp_classfy_value_store.append(int(i, 2))
                    else:
                        tmp_classfy_value_store.append(i)
                classfy_result.classfy_value_store = tmp_classfy_value_store

            self.value_store_list.append(classfy_result.classfy_value_store)

    def get_result(self):
        return self.result_frame

    def to_dataframe(self):

        index_arrays = [np.array(self.id_list), np.array(self.type_list)]
        index_tuple = list(zip(*index_arrays))
        index = pd.MultiIndex.from_tuples(index_tuple, names=['can_id', 'type'])

        data_matrix = np.array([self.begin_loc_list, self.length_list, self.score_list,
                                self.value_store_list],dtype=object)

        self.result_frame = pd.DataFrame(data_matrix.T, index=index,
                                         columns=['begin_loc', 'length', 'score', 'value_list'])
        self.result_frame.drop(index=5, level='type', inplace=True)
        return self.result_frame

    def get_sensor(self):
        sensor_dict = {}
        for i in range(len(self.type_list)):
            if self.type_list[i] == self.sensor_tag:
                canid = self.id_list[i]
                begin_byte = self.begin_loc_list[i] // 8
                if self.length_list[i] == 16:
                    byte_name = str(begin_byte) + str(begin_byte + 1)
                else:
                    byte_name = str(begin_byte)
                if canid in sensor_dict:
                    sensor_dict[canid].append(byte_name)
                else:
                    sensor_dict[canid] = [byte_name]
        return sensor_dict

