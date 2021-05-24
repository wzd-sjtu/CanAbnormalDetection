import csv
import pandas as pd
import numpy as np
import pickle
import copy
from matplotlib import pyplot as plt
from scipy import cluster
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import squareform
from sklearn.neighbors import LocalOutlierFactor
from .used_class import *

value_number = 96  # 比较重要的筛选参数
pre_value_number = 12
jump_value = 100
FCLUSTER_PARA = 0.75


class ParseCluster:
    def __init__(self, detect_data, sensor_dict):
        self.detect_data = detect_data
        self.sensor_dict = sensor_dict
        self.section_list = []
        self.data_matrix = None

    def generate_section_list(self):

        for canid in self.sensor_dict:
            for column in self.sensor_dict[canid]:
                self.section_list.append(canid + '_' + column)

    def generate_data_matrix(self):
        self.data_matrix = pd.DataFrame(columns=['time'])
        for canid in self.sensor_dict:
            canid_dataframe = self.detect_data[self.detect_data['can_id'] == canid]
            column_name_list = []
            merge_column_list = []
            new_name_dict = {}
            for column in self.sensor_dict[canid]:
                new_name_dict['data' + column] = canid + '_' + column
                if len(column) == 1:
                    column_name_list.append('data' + column)
                elif len(column) == 2:
                    column_name_list.append('data' + column[0])
                    column_name_list.append('data' + column[1])
                    merge_column_list.append(column)
            self.data_matrix = pd.concat([self.data_matrix, canid_dataframe.loc[:, ['time'] + column_name_list]])
            # self.data_matrix.reset_index(inplace=True, drop=True)
            # self.data_matrix = self.data_matrix.append(canid_dataframe.loc[:,['time']+column_name_list])

            for merge_colum in merge_column_list:
                column_name1 = 'data' + merge_colum[0]
                column_name2 = 'data' + merge_colum[1]
                self.data_matrix.loc[:, ['data' + merge_colum]] = \
                    self.data_matrix.loc[:, [column_name1]].values + self.data_matrix.loc[:, [column_name2]].values
                self.data_matrix.drop(columns=[column_name1, column_name2], inplace=True)

            self.data_matrix.rename(columns=new_name_dict, inplace=True)

        self.data_matrix.sort_values(by=['time'], inplace=True)
        self.data_matrix.fillna('-1', inplace=True)
        self.data_matrix[self.section_list] = self.data_matrix[self.section_list].apply(
            lambda x: x.astype(str).map(lambda x: int(x, base=16)))
        self.data_matrix.duplicated()
        self.data_matrix.replace(-1, np.nan, inplace=True)
        self.data_matrix.interpolate(limit_direction='both', inplace=True)

    def calculate_corr(self):
        self.result_matrix = self.data_matrix[self.section_list].corr()


    def cluster(self):
        # plot correlation matrix
        fig1 = plt.figure()  # 调用figure创建一个绘图对象
        ax = fig1.add_subplot(111)
        cax = ax.matshow(self.result_matrix, vmin=-1, vmax=1)  # 绘制热力图，从-1到1
        fig1.colorbar(cax)  # 将matshow生成热力图设置为颜色渐变条
        ticks = np.arange(0, len(self.section_list))  # 生成0-9，步长为1
        ax.set_xticks(ticks)  # 生成刻度
        ax.set_yticks(ticks)
        ax.set_xticklabels(self.section_list)  # 生成x轴标签
        ax.set_yticklabels(self.section_list)
        plt.xticks(rotation=90)

        dissimilarity = 1 - np.abs(self.result_matrix)  # 取绝对值，负相关也认为是相关
        hierarchy = linkage(squareform(dissimilarity), method='average')  # squareform用于压缩，linkage为层次聚类
        labels = fcluster(hierarchy, FCLUSTER_PARA, criterion='distance')  # 得到平面聚类
        print(labels)
        cluster_map = {}

        for cid, srcid in zip(labels, self.section_list):
            cluster_map[cid] = cluster_map.get(cid, []) + [srcid]

        print(cluster_map)
        fig2 = plt.figure(figsize=(25, 10))
        dn = dendrogram(hierarchy, labels=self.section_list)
        # plt.show()

        cluster_list = []
        for cluster in cluster_map:
            if len(cluster_map[cluster]) >= 5:
                cluster_list.append(cluster_map[cluster])
        cluster_array = np.asarray(cluster_list, dtype=object)
        self.cluster_array = cluster_array


    def run(self):
        self.generate_section_list()
        self.generate_data_matrix()
        self.calculate_corr()
        self.cluster()
        self.generate_snapshoot()
        self.fit_model()

    def get_cluster(self):
        return self.cluster_array

    def get_model(self):
        return self.lof_list

    def generate_snapshoot(self):

        self.shot_data_array_list = []
        for cluster in self.cluster_array:
            self.shot_data = pd.DataFrame(columns=['time'])
            shot_dict = {}
            canid_set = set()
            for segment in cluster:
                shot_dict[segment] = None
                canid_set.add(segment.split('_')[0])
            canid_list = list(canid_set)
            canid_list.sort()
            self.sensor_data = self.detect_data[self.detect_data['can_id'].isin(canid_set)]
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
                self.shot_data = pd.concat([self.shot_data, canid_dataframe.loc[:, ['time'] + column_name_list]])
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

            self.shot_data_array = self.shot_data[cluster].values
            self.shot_data_array_list.append(self.shot_data_array)

    def fit_model(self):
        self.lof_list = []
        for shot_data_array in self.shot_data_array_list:
            lof = LocalOutlierFactor(novelty=True)
            lof.fit(shot_data_array)
            y = lof.predict(shot_data_array)

            self.lof_list.append(lof)


