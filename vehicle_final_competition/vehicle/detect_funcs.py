# 存放用以检测数据的函数，返回报错信息
from .parse_funcs import correlation
from typing import Pattern
import numpy

import pandas as pd

from pandas import DataFrame

from keras.models import Sequential

from keras.layers import Dense

from keras.layers import LSTM

from keras.utils import np_utils

from keras.models import load_model

from keras.preprocessing.sequence import pad_sequences


def weightCalc(ID, interval, id_weight_stat):
    """Calculate the weight of the ID according to its interval"""
    mu = id_weight_stat[ID][0]
    sigma = id_weight_stat[ID][1]

    expo = (interval - mu)**2 / (2 * sigma * sigma)

    return expo


def detect_seq_id_statistics(global_data, id_weight_stat):
    anomalies = []
    threshold = 10

    idSet = set(id_weight_stat.keys())
    idInterval = {}  # id: last_occur
    weights = []

    TP = 0
    FP = 0
    TN = 0
    FN = 0

    for sd in global_data:
        No = int(sd.number)
        ID = sd.id
        ano = sd.anomaly
        time = sd.time

        if ID not in idSet:
            anomalies.append([ID, -1, No, time])
            continue

        if ID not in idInterval.keys():
            idInterval[ID] = No
        else:
            itv = No - idInterval[ID]
            idInterval[ID] = No

            weight = weightCalc(ID, itv, id_weight_stat)
            weights.append(weight)

            if weight >= threshold:
                anomalies.append([ID, itv, No, time])
    #             if str(ano) == '0':
    #                 FP += 1
    #             else:
    #                 TP += 1
    #                 # print(ID, itv, No, ano, weight)
    #         else:
    #             if str(ano) == '0':
    #                 TN += 1
    #             else:
    #                 FN += 1
    # TPR = TP / (TP + FN)
    # FPR = FP / (FP + TN)
    # print(threshold, TPR, FPR)

    # anomalies.append([tmpID, curr - prev, i.number, i.time])
    return anomalies  # html中通过 {{ dano.0 }} 调用此变量


def detect_seq_id_survival_rate(global_data, SR_dict):
    id_chunk = {}  # {ID: probability in a chunk, ...}
    length = len(global_data)
    chunk = SR_dict['chunk_len']
    # sig = 1 / chunk  # probability of one occurrence
    pos = 0  # global position
    chunk_pos = 0  # position in a chunk

    anomalies = []

    while pos < length:
        tmp_single_data = global_data[pos]
        ID = tmp_single_data.id
        if ID not in SR_dict.keys():
            pos += 1
            chunk_pos = (chunk_pos + 1) % chunk
            # unidentified
            continue

        if ID in id_chunk.keys():
            id_chunk[ID] += 1
        else:
            id_chunk[ID] = 1

        if chunk_pos == chunk - 1:
            for ID, prob in id_chunk.items():
                if prob > SR_dict[ID][1] or prob < SR_dict[ID][0]:
                    anomalies.append([ID, [global_data[pos - chunk + 1].time, tmp_single_data.time], round(prob, 2)])
            id_chunk.clear()
        pos += 1
        chunk_pos = (chunk_pos + 1) % chunk
    return anomalies  # html中通过 {{ dano.1 }} 调用此变量


def detect_seq_relative(global_data_detect, global_IDs_detect, cor_list):
    FV = [0, 0, 0, 0]  # num of distinct ID, num of msg, dlc Sum, Band Width
    idSet = []
    singleID = []
    cnt = float(global_data_detect[0].time)
    time_itv = 0.1
    min_cor = cor_list[0]
    max_cor = cor_list[1]

    appearTimes = {}
    s = set(global_IDs_detect)
    for i in s:
        appearTimes[i] = 0

    anomalies = []

    for line in global_data_detect:
        text = [line.time, line.id]
        if float(text[0]) > cnt + time_itv and FV[0] != 0:
            FV[1] = len(idSet)
            FV[2] = len(singleID)
            FV[3] = FV[3] / FV[0] / 10

            cor = correlation(FV)  # calculate correlation
            if cor < min_cor or cor > max_cor:
                anomalies.append([int(cnt / time_itv), [cnt, text[0]], cor])

            # reset
            cnt += time_itv
            FV = [0, 0, 0, 0]
            singleID = [text[1]]
            idSet = [text[1]]
            FV[0] += 1
        else:
            if text[1] not in singleID and appearTimes[text[1]] == 0:
                singleID.append(text[1])
                appearTimes[text[1]] = 1
            if text[1] in singleID:
                singleID.remove(text[1])
                appearTimes[text[1]] += 1
            if text[1] not in idSet:
                idSet.append(text[1])
            FV[0] += 1
            if "E+" in text[1]:
                tmp_id = text[1][0] + text[1][4] + text[1][7]
            else:
                tmp_id = text[1]
            FV[3] += int(tmp_id, 16)

    return anomalies  # html中通过 {{ dano.0 }} 调用此变量


def detect_seq_lstm(alphabet, letterRaw):
    model = load_model("./LSTMModel/model/")
    anomalies = []
    # alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # create mapping of characters to integers (0-25) and the reverse
    char_to_int = dict((c, i) for i, c in enumerate(alphabet))
    int_to_char = dict((i, c) for i, c in enumerate(alphabet))

    list = []
    for l in range(0, len(letterRaw) // 100 - 1):
        list.clear()
        pattern = []
        for j in range(0, 100):
            list.append(letterRaw[j + 100 * l].id)
        beginTime = letterRaw[100 * l].time
        endTime = letterRaw[100 * l + 99].time
        ifwrong = 0
        for m in range(0, 100):
            pattern.append([char_to_int[list[m]]])
        x = pad_sequences([pattern], maxlen=100, dtype='float32')
        x = numpy.reshape(pattern, (1, len(pattern), 1))
        x = x / float(len(alphabet))
        prediction = model.predict(x, verbose=0)
        index = numpy.argmax(prediction)
        result = int_to_char[index]
        seq_in = list
        if result != letterRaw[100 * l + 1].id:
            ifwrong = 1
        anomalies.append([beginTime, endTime, result, ifwrong])

    return anomalies
