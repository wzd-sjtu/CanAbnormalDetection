from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import os
import sys
from . import generalModels as gm
from . import parse_funcs as pf
from . import detect_funcs as df

from ParseDetect._parse_datafield import ParseData
from ParseDetect._detect_datafield import DatafieldDetect
from ParseDetect._parse_cluster import ParseCluster
from ParseDetect._detect_cluster import ClusterDetect
from ParseDetect.used_class import type_dict

from CanConstruct.code.AbnormalCreateClass import AttackCreate
from CanConstruct.code.LoadDataClass import LoadDataClass
from CanConstruct.code.BasicClass import DataFieldAttackInformation
import pandas as pd
import time

global_data = []
global_IDs = []
global_data_detect = []
global_IDs_detect = []
global_features = []

global_dataframe = None
data_rule_dataframe = None
global_detect_data_frame = None
cluster_model_list = None
cluster_array = None

datafield_deviant = None
cluster_deviant = None

loadDataExample = None
attackCreateExample = None # 使用的全局变量，可否用静态变量的方式存储？不清楚
allCanIdList = ['19E', '621', '601', '348', '60C', '481', '263', '604',
                 '17D', '19D', '1.00E+09', '34A', '19B', '140', '52A',
                 '3D1', '191', '269', '4C9', 'C5', '4F1', '3.00E+09',
                 'C1', '3.00E+05', '4D1', '565', 'C9', '194', '141', '1F5',
                 '1.00E+05', '608', '120', '1C6', '471', '230', 'E1', '603',
                 '1C3', '4C1', '128', '589', '1F1', '12A']


def instantiate_global_data(file):
    """ 读取正常数据集，实例化SingleData，将其加入global_data列表
        同时生成id列表 """
    global_data.clear()
    global_IDs.clear()
    raw_lines = file.readlines()
    raw_lines.pop(0)
    for line in raw_lines:
        items = line.decode('utf-8').strip().split(',')
        # hex_to_dec = int(items[2], 16)
        # dec_to_bin = bin(hex_to_dec)[2:]
        sd = gm.SingleData(items[0], items[2].upper(), items[1], items[3])
        global_data.append(sd)
        global_IDs.append(items[2].upper())

    global global_dataframe
    file.seek(0)
    global_dataframe = pd.read_csv(file, index_col=0)


def instantiate_global_data_detect(file):
    """ 读取待检测的数据集并实例化相应数据结构 """
    global_data_detect.clear()
    global_IDs_detect.clear()
    raw_lines = file.readlines()
    raw_lines.pop(0)
    for line in raw_lines:
        items = line.decode('utf-8').strip().split(',')
        # hex_to_dec = int(items[2], 16)
        # dec_to_bin = bin(hex_to_dec)[2:]
        sd = gm.SingleDataDetect(items[0], items[2].upper(), items[1], items[3])
        global_data_detect.append(sd)
        global_IDs_detect.append(items[2].upper())

    global global_detect_data_frame
    file.seek(0)
    global_detect_data_frame = pd.read_csv(file, index_col=0)


def home(request):
    return render(request, 'home.html', {'targetChoics': allCanIdList})


def parse(request):
    file = request.FILES.get('myfile')
    items = []
    if file:
        instantiate_global_data(file)
        return render(request, 'parse/parse.html', {'data': global_data, 'id': global_IDs, 'targetChoics': allCanIdList})
    else:
        return render(request, 'parse/parse.html', {'targetChoics': allCanIdList})


def _parse_sequence(request):
    global_features.clear()
    stat = pf.seq_id_statistics(global_IDs)
    sr = pf.seq_id_survival_rate(global_IDs)
    cos = pf.parse_seq_cos_sim(global_data)
    feat = gm.NormalSeqFeatures(stat, sr, cos)
    global_features.append(feat)
    return render(request, 'parse/sequence.html',
                  {'data': global_data, 'id': global_IDs, 'feat': global_features, 'targetChoics': allCanIdList}, )


def _parse_datafield(request):
    global data_rule_dataframe, global_dataframe
    global cluster_model_list, cluster_array
    prd = ParseData(global_dataframe)
    prd.run()
    data_rule_dataframe = prd.get_result()
    show_rule_dataframe = pd.DataFrame(data_rule_dataframe, copy=True)
    # show_rule_dataframe.rename(index=type_dict, inplace=True)

    sensor_dict = prd.get_sensor()
    sc = ParseCluster(global_dataframe, sensor_dict)
    sc.run()
    cluster_model_list = sc.get_model()
    cluster_array = sc.get_cluster()
    cluster_dict_array = []
    for cluster in cluster_array:
        cluster_dict_list = []
        for sing_cluster in cluster:
            canid, byte = sing_cluster.split('_')
            byte = "D" + byte
            tmp_dict = {
                'canid': canid,
                'byte': byte
            }
            cluster_dict_list.append(tmp_dict)
        cluster_dict_array.append(cluster_dict_list)
    return render(request, 'parse/datafield.html', {'data_rule': show_rule_dataframe, 'cluster_array': cluster_dict_array})


def detect(request):
    file = request.FILES.get('myfile')
    items = []
    if file:
        instantiate_global_data_detect(file)
        return render(request, 'detect/detect.html', {'ddata': global_data_detect, 'did': global_IDs_detect, 'targetChoics': allCanIdList})
    else:
        return render(request, 'detect/detect.html', {'targetChoics': allCanIdList})


def _detect_sequence(request):
    ano1 = df.detect_seq_id_statistics(global_data_detect, global_features[0].stat)
    ano2 = df.detect_seq_id_survival_rate(global_data_detect, global_features[0].SR)
    anomalies = [ano1, ano2]
    return render(request, 'detect/sequence.html',
                  {'ddata': global_data_detect, 'did': global_IDs_detect, 'dano': anomalies, 'targetChoics': allCanIdList})


def _detect_datafield(request):
    global datafield_deviant, global_detect_data_frame, data_rule_dataframe
    print(time.perf_counter())
    dd = DatafieldDetect(global_detect_data_frame, data_rule_dataframe)
    dd.run()
    print(time.perf_counter())
    datafield_deviant = dd.get_deviant()
    print(datafield_deviant)
    return render(request, 'detect/datafield.html',
                  {'datafield_deviant': datafield_deviant})


def _detect_sequenceRelationship(request):
    ano1 = df.detect_seq_cos_sim(global_data_detect, global_features[0].cosSim)
    anomalies = [ano1]
    return render(request, 'detect/seq_relate.html',
                  {'ddata': global_data_detect, 'did': global_IDs_detect, 'dano': anomalies, 'targetChoics': allCanIdList})


def _detect_datafieldRelationship(request):
    global global_detect_data_frame, cluster_deviant
    global cluster_model_list, cluster_array
    cd = ClusterDetect(cluster_array, global_detect_data_frame, cluster_model_list)
    cd.run()
    cluster_deviant = cd.get_deviant()
    print(cluster_deviant)
    return render(request, 'detect/df_relate.html',
                  {'cluster_deviant': cluster_deviant})




def work(request):
    return render(request, 'work.html', {'targetChoics': allCanIdList})


def about(request):
    return render(request, 'about.html', {'targetChoics': allCanIdList})


def contact(request):
    return render(request, 'contact.html', {'targetChoics': allCanIdList})


def rules(request):
    file = request.FILES.get('myfile')
    raw_lines = file.readlines()
    lines = []
    for line in raw_lines:
        lines.append(line.decode('utf-8').strip())
    return render(request, 'rules.html', {'file': lines[:10], 'targetChoics': allCanIdList})


def uniqueid(request):
    return render(request, 'uniqueid.html', {'targetChoics': allCanIdList})

def construct(request):

    # 数据导入，为接下来的攻击打下基础
    # 这里就不初始化数据了，防止出问题喽
    loadDataExample = LoadDataClass()
    loadDataExample.readHadCutData()
    attackCreateExample = AttackCreate()
    attackCreateExample.sourceDataSnippet = loadDataExample.sourceDataSnippet
    attackCreateExample.historyNormalDataSnippet = loadDataExample.historyNormalDataSnippet
    # 这里的load不知道如何导入呢？应当提供尽可能高的可用性


    return render(request, 'construct/construct.html')

# 报文网页可以一点点写，提高efficiency
def _construct_insert(request):
    # 传回了一个参数字典，我们需要设置下拉框选项
    return render(request, 'construct/construct_insert.html', {'targetChoics': allCanIdList})
def insert_attack(request):
    if request.is_ajax():
        print(request.POST)
        # formdata.append("chose_id", $("#chose_id").val());
        # formdata.append("attack_exist_time", $("#attack_exist_time").val());

        # 实际上，这里的js是存在很大的问题的？感觉稍微有点裂开？
        chose_id = request.POST.get('chose_id')
        chose_attack_exist_time = request.POST.get('attack_exist_time')
        chose_attack_cycle_time = request.POST.get('attack_cycle_time')

        # 数据需要重新导入？我真的是醉了
        # 这种时候，最好再开一个进程进行处理，这样算是比较稳妥的

        loadDataExample = LoadDataClass()
        loadDataExample.readHadCutData()
        attackCreateExample = AttackCreate()
        attackCreateExample.sourceDataSnippet = loadDataExample.sourceDataSnippet
        attackCreateExample.historyNormalDataSnippet = loadDataExample.historyNormalDataSnippet

        # def insert_attack(self, id, normal_T, ratio, exist_time):
        attackCreateExample.insert_attack(str(chose_id), float(chose_attack_cycle_time), 1, float(chose_attack_exist_time))
        tmp = pd.read_csv('./CanConstruct/src/attackDescription/myDescription.csv')
        # 获得log信息，是可信的
        target_dict = {}
        num = tmp.shape[0]
        target_dict['size'] = str(num)
        # 不妨存储为一个小小的字典哦
        for i in range(0, num):
            time_loc = "time" + str(i)
            target_dict[time_loc] = str(tmp.iloc[i]['time'])
            can_id_loc = "can_id" + str(i)
            target_dict[can_id_loc] = str(tmp.iloc[i]['can_id'])
            data_loc = "data_in_hex" + str(i)
            target_dict[data_loc] = str(tmp.iloc[i]['data_in_hex'])
            description_loc = "erase_attack"
            target_dict[description_loc] = "insert attack"

        response = JsonResponse(target_dict)

        return response
    # 以下才是较为标准的写法，这点谨记
    #response = JsonResponse({"status": '服务器接收成功', 'data': data, 'list': list})
    #return response

def _construct_erase(request):
    return render(request, 'construct/construct_erase.html', {'targetChoics': allCanIdList})
def erase_attack(request):
    if request.is_ajax():
        print(request.POST)
        # formdata.append("chose_id", $("#chose_id").val());
        # formdata.append("attack_exist_time", $("#attack_exist_time").val());

        # 实际上，这里的js是存在很大的问题的？感觉稍微有点裂开？
        chose_id = request.POST.get('chose_id')
        chose_attack_exist_time = request.POST.get('attack_exist_time')
        print(chose_attack_exist_time)
        print(chose_id)

        # 数据需要重新导入？我真的是醉了
        # 这种时候，最好再开一个进程进行处理，这样算是比较稳妥的

        loadDataExample = LoadDataClass()
        loadDataExample.readHadCutData()
        attackCreateExample = AttackCreate()
        attackCreateExample.sourceDataSnippet = loadDataExample.sourceDataSnippet
        attackCreateExample.historyNormalDataSnippet = loadDataExample.historyNormalDataSnippet

        attackCreateExample.erase_attack(str(chose_id), float(chose_attack_exist_time))
        tmp = pd.read_csv('./CanConstruct/src/attackDescription/myDescription.csv')

        target_dict = {}
        num = tmp.shape[0]
        target_dict['size'] = str(num)
        # 不妨存储为一个小小的字典哦
        for i in range(0, num):
            time_loc = "time" + str(i)
            target_dict[time_loc] = str(tmp.iloc[i]['time'])
            can_id_loc = "can_id" + str(i)
            target_dict[can_id_loc] = str(tmp.iloc[i]['can_id'])
            data_loc = "data_in_hex" + str(i)
            target_dict[data_loc] = str(tmp.iloc[i]['data_in_hex'])
            description_loc = "description" + str(i)
            target_dict[description_loc] = str(tmp.iloc[i]['description'])

        response = JsonResponse(target_dict)

        return response

def _construct_reput(request):
    return render(request, 'construct/construct_reput.html', {'targetChoics': allCanIdList})
def _construct_reput_single(request):
    return render(request, 'construct/construct_reput_single.html', {'targetChoics': allCanIdList})
def _construct_reput_all(request):
    return render(request, 'construct/construct_reput_all.html', {'targetChoics': allCanIdList})
# 一般来说，重放攻击的代码量是比较小的，远远没有现在这么大的
# 这里写的可视化过程是非常复杂的，某种程度上来说，是难以理解的
def reput_attack(request):
    if request.is_ajax():
        print(request.POST)
        # formdata.append("chose_id", $("#chose_id").val());
        # formdata.append("attack_exist_time", $("#attack_exist_time").val());

        # 实际上，这里的js是存在很大的问题的？感觉稍微有点裂开？
        chose_id = request.POST.get('chose_id')
        chose_attack_exist_time = request.POST.get('attack_exist_time')
        if chose_id == 'undefined':
            # 调用别的手段即可，根据参数做出不同选择
            # chose_id需要给出参数？

            loadDataExample = LoadDataClass()
            loadDataExample.readHadCutData()
            attackCreateExample = AttackCreate()
            attackCreateExample.sourceDataSnippet = loadDataExample.sourceDataSnippet
            attackCreateExample.historyNormalDataSnippet = loadDataExample.historyNormalDataSnippet

            attackCreateExample.reput_attack_AllData(float(chose_attack_exist_time))
            tmp = pd.read_csv('./CanConstruct/src/attackDescription/myDescription.csv')

            target_dict = {}
            num = tmp.shape[0]
            target_dict['size'] = str(num)
            # 不妨存储为一个小小的字典哦
            for i in range(0, num):
                time_loc = "time" + str(i)
                target_dict[time_loc] = str(tmp.iloc[i]['time'])
                can_id_loc = "can_id" + str(i)
                target_dict[can_id_loc] = str(tmp.iloc[i]['can_id'])
                data_loc = "data_in_hex" + str(i)
                target_dict[data_loc] = str(tmp.iloc[i]['data_in_hex'])
                description_loc = "erase_attack"
                target_dict[description_loc] = "reput attack"

            response = JsonResponse(target_dict)

            return response
        # 数据需要重新导入？我真的是醉了
        # 这种时候，最好再开一个进程进行处理，这样算是比较稳妥的
        else:
            loadDataExample = LoadDataClass()
            loadDataExample.readHadCutData()
            attackCreateExample = AttackCreate()
            attackCreateExample.sourceDataSnippet = loadDataExample.sourceDataSnippet
            attackCreateExample.historyNormalDataSnippet = loadDataExample.historyNormalDataSnippet

            attackCreateExample.reput_attack_SingleId(str(chose_id), float(chose_attack_exist_time))
            tmp = pd.read_csv('./CanConstruct/src/attackDescription/myDescription.csv')

            target_dict = {}
            num = tmp.shape[0]
            target_dict['size'] = str(num)
            # 不妨存储为一个小小的字典哦
            for i in range(0, num):
                time_loc = "time" + str(i)
                target_dict[time_loc] = str(tmp.iloc[i]['time'])
                can_id_loc = "can_id" + str(i)
                target_dict[can_id_loc] = str(tmp.iloc[i]['can_id'])
                data_loc = "data_in_hex" + str(i)
                target_dict[data_loc] = str(tmp.iloc[i]['data_in_hex'])
                description_loc = "erase_attack"
                target_dict[description_loc] = "reput attack"

            response = JsonResponse(target_dict)

            return response
    # 以下才是较为标准的写法，这点谨记
    #response = JsonResponse({"status": '服务器接收成功', 'data': data, 'list': list})
    #return response

def _construct_changeDataField(request):
    return render(request, 'construct/construct_changeDataField.html', {'targetChoics': allCanIdList})
def changeDataField_attack(request):
    '''
    formdata.append("chose_id", $("#chose_id").val());
    formdata.append("attack_exist_time", $("#attack_exist_time").val());
    formdata.append("chose_attack_method", $("#chose_attack_method").val());
    formdata.append("sensor_attack_type", $("#sensor_attack_type").val());
    '''
    if request.is_ajax():
        print(request.POST)

        chose_id = request.POST.get('chose_id')
        chose_attack_exist_time = request.POST.get('attack_exist_time')
        chose_attack_method = request.POST.get('chose_attack_method')
        chose_sensor_attack_type = request.POST.get('sensor_attack_type')

        loadDataExample = LoadDataClass()
        loadDataExample.readHadCutData()
        attackCreateExample = AttackCreate()
        attackCreateExample.sourceDataSnippet = loadDataExample.sourceDataSnippet
        attackCreateExample.historyNormalDataSnippet = loadDataExample.historyNormalDataSnippet

        if chose_attack_method == "RanDom":
            attackCreateExample.changedatafield_attack_randomly(str(chose_id), float(chose_attack_exist_time))
        elif chose_attack_method == "ConstOrMultivalue":
            attackCreateExample.changedatafield_attack_const_or_multivalue(str(chose_id), float(chose_attack_exist_time))
        elif chose_attack_method == "Sensor":
            tyty = 0
            if chose_sensor_attack_type == "max-value":
                tyty = 0
            elif chose_sensor_attack_type == "min-value":
                tyty = 1
            elif chose_sensor_attack_type == "random-value":
                tyty = 2
            elif chose_sensor_attack_type == "advanced-attack":
                tyty = 3
            attackCreateExample.changedatafield_attack_sensro(str(chose_id), float(chose_attack_exist_time), tyty)

        # 数据需要重新导入？我真的是醉了
        # 这种时候，最好再开一个进程进行处理，这样算是比较稳妥的
        # 制造完攻击后，将内容log直接提取出来即可
        tmp = pd.read_csv('./CanConstruct/src/attackDescription/myDescription.csv')

        target_dict = {}
        num = tmp.shape[0]
        target_dict['size'] = str(num)
        # 不妨存储为一个小小的字典哦
        for i in range(0, num):
            time_loc = "time" + str(i)
            target_dict[time_loc] = str(tmp.iloc[i]['time'])
            can_id_loc = "can_id" + str(i)
            target_dict[can_id_loc] = str(tmp.iloc[i]['can_id'])
            data_loc = "data_in_hex" + str(i)
            target_dict[data_loc] = str(tmp.iloc[i]['data_in_hex'])
            description_loc = "description" + str(i)
            target_dict[description_loc] = str(tmp.iloc[i]['description'])

        response = JsonResponse(target_dict)

        return response
    # 以下才是较为标准的写法，这点谨记
    #response = JsonResponse({"status": '服务器接收成功', 'data': data, 'list': list})
    #return response

# 至此，写完了这个非常复杂的attack_make函数，逻辑稍微有点复杂
def attack_make(request):
    # 这里涉及到了攻击的制造，需要写很多代码？
    if request.is_ajax():
        print(request.POST)

        # 一共收集到五个信息？是合理的哦
        chose_attack_type = request.POST.get('chose_attack_type')
        chose_attack_exist_time = request.POST.get('attack_exist_time')
        chose_id = request.POST.get('chose_id')
        chose_datafield_attack_method = request.POST.get('chose_datafield_attack_method')
        chose_sensor_attack_type = request.POST.get('sensor_attack_type')
        chose_attack_cycle_time = request.POST.get('chose_cycle_time')
        # 数据导入
        loadDataExample = LoadDataClass()
        loadDataExample.readHadCutData()
        attackCreateExample = AttackCreate()
        attackCreateExample.sourceDataSnippet = loadDataExample.sourceDataSnippet
        attackCreateExample.historyNormalDataSnippet = loadDataExample.historyNormalDataSnippet


        if chose_attack_type == "注入insert":
            attackCreateExample.insert_attack(str(chose_id), float(chose_attack_cycle_time), 1,
                                              float(chose_attack_exist_time))
        elif chose_attack_type == "删除erase":
            attackCreateExample.erase_attack(str(chose_id), float(chose_attack_exist_time))
        elif chose_attack_type == "重放单个id_reput":
            attackCreateExample.reput_attack_SingleId(str(chose_id), float(chose_attack_exist_time))
        elif chose_attack_type == "重放多个id_reput":
            attackCreateExample.reput_attack_AllData(float(chose_attack_exist_time))
        elif chose_attack_type == "数据域修改":
            if chose_datafield_attack_method == "随即修改RanDom":
                attackCreateExample.changedatafield_attack_randomly(str(chose_id), float(chose_attack_exist_time))
            elif chose_datafield_attack_method == "定值或多值字段修改":
                attackCreateExample.changedatafield_attack_const_or_multivalue(str(chose_id),float(chose_attack_exist_time))
            elif chose_datafield_attack_method == "传感器修改Sensor":
                # 具体的攻击逻辑存储在后台的类里面，并不存在于这里的
                tyty = 0
                if chose_sensor_attack_type == "max-value":
                    tyty = 0
                elif chose_sensor_attack_type == "min-value":
                    tyty = 1
                elif chose_sensor_attack_type == "random-value":
                    tyty = 2
                elif chose_sensor_attack_type == "advanced-attack":
                    tyty = 3
                attackCreateExample.changedatafield_attack_sensro(str(chose_id), float(chose_attack_exist_time), tyty)
        tmp = pd.read_csv('./CanConstruct/src/attackDescription/myDescription.csv')

        target_dict = {}
        num = tmp.shape[0]
        target_dict['size'] = str(num)
        # 不妨存储为一个小小的字典哦
        # 总而言之，异常信息是存进去了，暂时不知道如何展示？
        for i in range(0, num):
            time_loc = "time" + str(i)
            target_dict[time_loc] = str(tmp.iloc[i]['time'])
            can_id_loc = "can_id" + str(i)
            target_dict[can_id_loc] = str(tmp.iloc[i]['can_id'])
            data_loc = "data_in_hex" + str(i)
            target_dict[data_loc] = str(tmp.iloc[i]['data_in_hex'])
            description_loc = "description" + str(i)
            target_dict[description_loc] = str(tmp.iloc[i]['description'])

        response = JsonResponse(target_dict)

        return response


def _construct_about(request):
    return render(request, 'construct/construct_about.html')

def complete_system(request):
    return render(request, 'CompleteRow/complete.html', {'targetChoics': allCanIdList})


def first_detect(request):
    # 这里涉及到了攻击的制造，需要写很多代码？
    target_list = {}
    if request.is_ajax():
        response = JsonResponse(target_list)
        return response
def second_detect(request):
    # 这里涉及到了攻击的制造，需要写很多代码？
    target_list = {}
    if request.is_ajax():
        response = JsonResponse(target_list)
        return response

def third_detect(request):
    # 这里涉及到了攻击的制造，需要写很多代码？
    target_list = {}
    if request.is_ajax():
        response = JsonResponse(target_list)
        return response

def fourth_detect(request):
    # 这里涉及到了攻击的制造，需要写很多代码？
    target_list = {}
    if request.is_ajax():
        response = JsonResponse(target_list)
        return response