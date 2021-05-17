from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
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
    loadDataExample = LoadDataClass()
    loadDataExample.readHadCutData()
    attackCreateExample = AttackCreate()
    attackCreateExample.sourceDataSnippet = loadDataExample.sourceDataSnippet
    attackCreateExample.historyNormalDataSnippet = loadDataExample.historyNormalDataSnippet
    # 这里的load不知道如何导入呢？应当提供尽可能高的可用性


    return render(request, 'construct/construct.html')

# 以下是报文的攻击页面？需要根据不同的点击，返回不同的信息？
def _construct_insert(request):
    # 传回了一个参数字典，我们需要设置下拉框选项
    return render(request, 'construct/construct_insert.html', {'targetChoics': allCanIdList})
def process(request):
    if request.is_ajax():
        print(request.POST)
        # formdata.append("chose_id", $("#chose_id").val());
        # formdata.append("attack_exist_time", $("#attack_exist_time").val());

        # 实际上，这里的js是存在很大的问题的？感觉稍微有点裂开？
        chose_id = request.POST.get('chose_id')
        chose_attack_exist_time = request.POST.get('attack_exist_time')
        print(chose_attack_exist_time)
        print(chose_id)
        attackCreateExample.erase_attack(str(chose_id), float(chose_attack_exist_time))
        tmp = pd.read_csv('./CanConstruct/src/attackDescription/myDescription.csv')
        target_list = []
        for i in range(0, tmp.shape[0]):
            desc = "time is "
            desc = desc + tmp.iloc[i]['time']
            desc = desc + " id is "
            desc = desc + tmp.iloc[i]['can_id']
            desc = desc + "  " + tmp.iloc[i]['description']
            target_list.append(desc)
        return render(request, 'construct/construct_insert.html', {'targetChoics': allCanIdList, 'Description':target_list})

def _construct_erase(request):
    return render(request, 'construct/construct_erase.html')
def _construct_reput(request):
    return render(request, 'construct/construct_reput.html')
def _construct_changeDataField(request):
    return render(request, 'construct/construct_changeDataField.html')
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
