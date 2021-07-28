import pandas as pd
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import os
import sys

from ParseDetect._parse_datafield import ParseData
from ParseDetect._detect_datafield import DatafieldDetect
from ParseDetect._parse_cluster import ParseCluster
from ParseDetect._detect_cluster import ClusterDetect
from ParseDetect.used_class import type_dict

from CanConstruct.code.AbnormalCreateClass import AttackCreate
from CanConstruct.code.LoadDataClass import LoadDataClass
from CanConstruct.code.BasicClass import DataFieldAttackInformation
import pandas as pd
import numpy as np
import time
import pickle

# rule_data = pd.read_pickle('./src/_parse_rule.pkl')
# 这里就是标准的分区间格式信息，不需要操作别的内容了
# print(rule_data)
cluster_array = np.load('./src/cluster_array.npy', allow_pickle=True)
print(cluster_array)