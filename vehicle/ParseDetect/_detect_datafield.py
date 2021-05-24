# from used_class import *
from numpy import byte
import pandas as pd
from scipy.cluster.hierarchy import single
import time
from .used_class import *

deviant_description = {
    1: ' A strange ID',
    2: 'Checksum error',
    3: 'The sensor changes too sharp',
    4: 'The sensor is out of range',
    5: 'The constant has changed',
    6: 'Counter error',
    7: 'Multi-value error'
}


class DatafieldDetect:
    def __init__(self, detect_data, rule_data):
        self.detect_data = detect_data
        self.rule_data = pd.DataFrame(rule_data, copy=True)
        self.rule_data.reset_index(level='type', inplace=True)
        self.rule_data.loc[:, 'value_list'] = self.rule_data.loc[:, 'value_list'].apply(lambda x: str(x))
        self.true_pos_list = []
        self.false_pos_list = []
        self.true_neg_list = []
        self.false_neg_list = []
        self.canIDset = set(self.rule_data.index)
        self.last_data_dict = {}
        column_list = list(self.detect_data.columns) + ['Description']
        self.deviant_data = pd.DataFrame(columns=column_list)
        self.deviant_index = 0

    def run(self):
        for index, row in self.detect_data.iterrows():
            if row['can_id'] not in self.canIDset:
                self.add_to_deviant(row, UNCOMMON_ID, 0)
            else:
                self.line_detect(row)

    def line_detect(self, row):
        single_id_rule = self.rule_data.loc[[row['can_id']], :]
        if isinstance(single_id_rule, pd.DataFrame):
            pass
        else:
            single_id_rule = single_id_rule.to_frame()

        for index, single_rule in single_id_rule.iterrows():

            if single_rule['type'] == CHECKSUM_TAG:
                self.checksum(row, single_rule)
            elif single_rule['type'] == SENSOR_TAG:
                self.sensor(row, single_rule)
            elif single_rule['type'] == CONST_TAG:
                self.const(row, single_rule)
            elif single_rule['type'] == COUNTER_TAG:
                self.counter(row, single_rule)
            elif single_rule['type'] == MULTI_VALUE_TAG:
                self.mutiple(row, single_rule)

    def sensor(self, row, single_rule):
        sen_min, sen_max, sen_grad = single_rule['value_list'][1:-1].split(',')
        sen_min = int(sen_min)
        sen_max = int(sen_max)
        sen_grad = int(sen_grad)
        begin_loc = single_rule['begin_loc']
        end_loc = single_rule['length'] + single_rule['begin_loc'] - 1
        sen_data = int(row['data_in_binary'][begin_loc:end_loc + 1], 2)
        segname = row['can_id'] + str(single_rule['begin_loc'])
        if segname not in self.last_data_dict:
            self.last_data_dict[segname] = sen_data
        else:
            diff = self.last_data_dict[segname] - sen_data
            self.last_data_dict[segname] = sen_data
            if abs(diff) > sen_grad:
                self.add_to_deviant(row, SENSOR_TOO_SHARP, single_rule['begin_loc'])

        if not sen_min <= sen_data <= sen_max:
            self.add_to_deviant(row, SENSOR_OUT_RANGE)

    def const(self, row, single_rule):
        normal_data = int(single_rule['value_list'][1:-1])
        begin_loc = single_rule['begin_loc']
        end_loc = single_rule['length'] + single_rule['begin_loc'] - 1
        con_data = int(row['data_in_binary'][begin_loc:end_loc + 1], 2)

        if con_data != normal_data:
            self.add_to_deviant(row, CONST_ERROR, single_rule['begin_loc'])

    def counter(self, row, single_rule):
        segname = row['can_id'] + str(single_rule['begin_loc'])
        end_loc = single_rule['length'] + single_rule['begin_loc'] - 1
        cou_data = int(row['data_in_binary'][single_rule['begin_loc']:end_loc + 1], 2)
        cou_length = single_rule['length']
        if segname not in self.last_data_dict:
            self.last_data_dict[segname] = cou_data
        else:
            diff = (cou_data - self.last_data_dict[segname]) % (2 ** cou_length)
            self.last_data_dict[segname] = cou_data
            if diff != 1:
                self.add_to_deviant(row, COUNTER_ERROR, single_rule['begin_loc'])

    def mutiple(self, row, single_rule):
        multiple_list = single_rule['value_list'][1:-1].split(',')
        multiple_list = list(map(int, multiple_list))
        end_loc = single_rule['length'] + single_rule['begin_loc'] - 1
        mul_data = int(row['data_in_binary'][single_rule['begin_loc']:end_loc + 1], 2)

        if mul_data not in multiple_list:
            self.add_to_deviant(row, MULTI_ERROR, single_rule['begin_loc'])

    def checksum(self, row, single_rule):
        byte_sum = 0
        for i in range(0, row['length']):
            byte_sum += int(row['data' + str(i)], 16)
        checkpos = single_rule['begin_loc'] // 8
        byte_sum = (byte_sum - int(row['data' + str(checkpos)], 16)) % 256
        if byte_sum == int(row['data' + str(checkpos)], 16):
            return 0
        else:
            self.add_to_deviant(row, CHECKSUM_ERROR, single_rule['begin_loc'])

    def add_to_deviant(self, row, deviant_type, begin_loc):
        single_description = "The devient starts at " + str(begin_loc) + '.' \
                             + deviant_description[deviant_type]
        tmp_list = row.values.tolist() + [single_description]
        self.deviant_data.loc[self.deviant_index] = tmp_list
        self.deviant_index += 1

    def get_deviant(self):
        return self.deviant_data
