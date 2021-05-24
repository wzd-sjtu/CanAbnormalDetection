import csv
import pandas as pd
import numpy as np
import copy
from matplotlib import pyplot as plt
from scipy import cluster
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import squareform
from sklearn.neighbors import LocalOutlierFactor
from .used_class import *
import pickle


class ClusterDetect:
    def __init__(self, cluster_array, detect_data, lof_list):
        self.cluster_array = cluster_array
        self.detect_data = detect_data
        self.lof_list = lof_list
        self.deviant_data = None

    def run(self):
        self.generate_snapshoot()
        self.predict()

    def get_deviant(self):
        return self.deviant_data

    def predict(self):
        # label，也就是anormal，0表示正常，非0表示异常，
        # pred，1表示正常，-1表示异常
        self.truepos_list = []
        self.falsepos_list = []
        self.trueneg_list = []
        self.falseneg_list = []

        for lof, shot_data_array, label, _time in zip(self.lof_list, self.shot_data_array_list, self.label_list,
                                                      self.time_list):

            pred = lof.predict(shot_data_array)
            for l_pred, l_label, l_time in zip(pred, label, _time):
                if l_pred == -1 and label != 0:
                    self.truepos_list.append(l_time)
                elif l_pred == -1 and label == 0:
                    self.falsepos_list.append(l_time)
                elif l_pred == 1 and label != 0:
                    self.trueneg_list.append(l_time)
                elif l_pred == 1 and label == 0:
                    self.falseneg_list.append(l_time)
        all_pos_list = self.truepos_list + self.falsepos_list
        self.deviant_data = pd.DataFrame(self.detect_data[self.detect_data['time'].isin(all_pos_list)])
        self.deviant_data['Description'] = 'Outlier values.'

    def generate_snapshoot(self):
        self.shot_data_array_list = []
        self.label_list = []
        self.time_list = []
        for cluster in self.cluster_array:
            self.shot_data = pd.DataFrame(columns=['time', 'anormaly'])
            shot_dict = {}
            canid_set = set()
            for segment in cluster:
                shot_dict[segment] = None
                canid_set.add(segment.split('_')[0])

            self.sensor_data = self.detect_data[self.detect_data['can_id'].isin(canid_set)]
            canid_list = list(canid_set)
            canid_list.sort()
            for canid in canid_list:
                canid_dataframe = self.sensor_data[self.sensor_data['can_id'] == canid]
                column_name_list = []
                merge_column_list = []
                new_name_dict = {}
                for segment in cluster:
                    canid_2, column = segment.split('_')
                    if canid_2 != canid:
                        continue

                    new_name_dict['data' + column] = canid + '_' + column
                    if len(column) == 1:
                        column_name_list.append('data' + column)
                    elif len(column) == 2:
                        column_name_list.append('data' + column[0])
                        column_name_list.append('data' + column[1])
                        merge_column_list.append(column)
                self.shot_data = pd.concat(
                    [self.shot_data, canid_dataframe.loc[:, ['time', 'anormal'] + column_name_list]])
                # self.sensor_data.reset_index(inplace=True, drop=True)
                # self.sensor_data = self.sensor_data.append(canid_dataframe.loc[:,['time']+column_name_list])
                for merge_colum in merge_column_list:
                    column_name1 = 'data' + merge_colum[0]
                    column_name2 = 'data' + merge_colum[1]
                    self.shot_data.loc[:, ['data' + merge_colum]] = \
                        self.shot_data.loc[:, [column_name1]].values + \
                        self.shot_data.loc[:, [column_name2]].values
                    self.shot_data.drop(columns=[column_name1, column_name2], inplace=True)
                self.shot_data.rename(columns=new_name_dict, inplace=True)

            self.shot_data = self.shot_data.fillna('-1')
            self.shot_data[cluster] = self.shot_data[cluster].apply(
                lambda x: x.astype(str).map(lambda x: int(x, base=16)))

            self.shot_data = self.shot_data.replace(-1, np.nan)

            self.shot_data.interpolate(method='pad', inplace=True)

            self.shot_data.dropna(inplace=True)
            label = list(self.shot_data['anormal'])
            _time = self.shot_data['time']
            self.label_list.append(label)
            self.time_list.append(_time)
            self.shot_data_array = self.shot_data[cluster].values
            self.shot_data_array_list.append(self.shot_data_array)

