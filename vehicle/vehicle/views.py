from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import os
import sys
from . import generalModels as gm

from CanConstruct.code.AbnormalCreateClass import AttackCreate
from CanConstruct.code.LoadDataClass import LoadDataClass
from CanConstruct.code.BasicClass import DataFieldAttackInformation
import pandas as pd

global_data = []
loadDataExample = None
attackCreateExample = None # 使用的全局变量，可否用静态变量的方式存储？不清楚
allCanIdList = ['19E', '621', '601', '348', '60C', '481', '263', '604',
                 '17D', '19D', '1.00E+09', '34A', '19B', '140', '52A',
                 '3D1', '191', '269', '4C9', 'C5', '4F1', '3.00E+09',
                 'C1', '3.00E+05', '4D1', '565', 'C9', '194', '141', '1F5',
                 '1.00E+05', '608', '120', '1C6', '471', '230', 'E1', '603',
                 '1C3', '4C1', '128', '589', '1F1', '12A']


def instantiate_glabal_data(file):
    """Read from dataset and instantiate global_data with SingleData"""
    global_data.clear()
    raw_lines = file.readlines()
    raw_lines.pop(0)
    for line in raw_lines:
        items = line.decode('utf-8').strip().split(',')
        hex_to_dec = int(items[2], 16)
        dec_to_bin = bin(hex_to_dec)[2:]
        sd = gm.SingleData(items[1], items[3], items[2], dec_to_bin)
        global_data.append(sd)


def home(request):
    return render(request, 'home.html')


def parse(request):
    file = request.FILES.get('myfile')
    items = []
    if file:
        instantiate_glabal_data(file)
        return render(request, 'parse/parse.html', {'parse': global_data})
    else:
        return render(request, 'parse/parse.html')


def _parse_sequence(request):
    return render(request, 'parse/sequence.html', {'parse': global_data})


def _parse_datafield(request):
    return render(request, 'parse/datafield.html', {'parse': global_data})


def detect(request):
    file = request.FILES.get('myfile')
    items = []
    if file:
        instantiate_glabal_data(file)
        return render(request, 'detect/detect.html', {'detect': global_data})
    else:
        return render(request, 'detect/detect.html')


def _detect_sequence(request):
    return render(request, 'detect/sequence.html', {'detect': global_data})


def _detect_datafield(request):
    return render(request, 'detect/datafield.html', {'detect': global_data})


def _detect_sequenceRelationship(request):
    return render(request, 'detect/seq_relate.html', {'detect': global_data})


def _detect_datafieldRalationship(request):
    return render(request, 'detect/df_relate.html', {'detect': global_data})


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
            target_dict[time_loc] = tmp.iloc[i]['time']
            can_id_loc = "can_id" + str(i)
            target_dict[can_id_loc] = tmp.iloc[i]['can_id']
            data_loc = "data_in_hex" + str(i)
            target_dict[data_loc] = tmp.iloc[i]['data_in_hex']
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
            target_dict[time_loc] = tmp.iloc[i]['time']
            can_id_loc = "can_id" + str(i)
            target_dict[can_id_loc] = tmp.iloc[i]['can_id']
            data_loc = "data_in_hex" + str(i)
            target_dict[data_loc] = tmp.iloc[i]['data_in_hex']
            description_loc = "erase_attack"
            target_dict[description_loc] = "erase attack"

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
                target_dict[time_loc] = tmp.iloc[i]['time']
                can_id_loc = "can_id" + str(i)
                target_dict[can_id_loc] = tmp.iloc[i]['can_id']
                data_loc = "data_in_hex" + str(i)
                target_dict[data_loc] = tmp.iloc[i]['data_in_hex']
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
                target_dict[time_loc] = tmp.iloc[i]['time']
                can_id_loc = "can_id" + str(i)
                target_dict[can_id_loc] = tmp.iloc[i]['can_id']
                data_loc = "data_in_hex" + str(i)
                target_dict[data_loc] = tmp.iloc[i]['data_in_hex']
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
            target_dict[time_loc] = tmp.iloc[i]['time']
            can_id_loc = "can_id" + str(i)
            target_dict[can_id_loc] = tmp.iloc[i]['can_id']
            data_loc = "data_in_hex" + str(i)
            target_dict[data_loc] = tmp.iloc[i]['data_in_hex']
            description_loc = "erase_attack"
            target_dict[description_loc] = "erase attack"

        response = JsonResponse(target_dict)

        return response
    # 以下才是较为标准的写法，这点谨记
    #response = JsonResponse({"status": '服务器接收成功', 'data': data, 'list': list})
    #return response

def _construct_about(request):
    return render(request, 'construct/construct_about.html')

def work(request):
    return render(request, 'work.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def rules(request):
    file = request.FILES.get('myfile')
    raw_lines = file.readlines()
    lines = []
    for line in raw_lines:
        lines.append(line.decode('utf-8').strip())
    return render(request, 'rules.html', {'file': lines[:10]})


def uniqueid(request):
    return render(request, 'uniqueid.html')
