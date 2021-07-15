# 存放用以检测数据的函数，返回报错信息
from .parse_funcs import cos_sim
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


def detect_seq_id_statistics(global_data, idFinalStat):
    idAppear = {}  # ID: prev, curr
    uniqueIDs = idFinalStat.keys()

    anomalies = []

    for i in global_data:
        tmpID = i.id
        if tmpID not in uniqueIDs:
            anomalies.append([tmpID, -1, i.number, i.time])
            continue
        elif tmpID not in idAppear.keys():
            idAppear[tmpID] = [i.number, i.number]
        else:
            prev = int(idAppear[tmpID][1])
            curr = int(i.number)
            idAppear[tmpID] = [prev, curr]
            if curr - prev < idFinalStat[tmpID][2] or curr - prev > idFinalStat[tmpID][3]:
                anomalies.append([tmpID, curr - prev, i.number, i.time])
    return anomalies  # html中通过 {{ dano.0 }} 调用此变量


def detect_seq_id_survival_rate(global_data, SRDict):
    idChunk = {}  # {ID: probability in a chunk, ...}
    length = len(global_data)
    chunk = 100
    sig = 1 / chunk  # probability of one occurrence
    pos = 0  # global position
    chunkPos = 0  # position in a chunk

    anomalies = []

    while pos < length:
        tmpSingleData = global_data[pos]
        ID = tmpSingleData.id
        if ID not in SRDict.keys():
            pos += 1
            chunkPos = (chunkPos + 1) % chunk
            continue

        if ID in idChunk.keys():
            idChunk[ID] += sig
        else:
            idChunk[ID] = sig

        if chunkPos == chunk - 1:
            for ID, prob in idChunk.items():
                if prob > SRDict[ID][1] or prob < SRDict[ID][0]:
                    anomalies.append([ID, [global_data[pos - 99].time, tmpSingleData.time], round(prob, 2)])
            idChunk.clear()
        pos += 1
        chunkPos = (chunkPos + 1) % chunk
    return anomalies  # html中通过 {{ dano.1 }} 调用此变量


def detect_seq_cos_sim(global_data_detect, CSlist):
    FV = [0, 0, 0, 0]  # num of distinct ID, num of msg, dlc Sum, Band Width
    idSet = []
    cnt = 0
    time_itv = 0.01
    minCS = CSlist[0]
    maxCS = CSlist[1]

    initTime = ''

    anomalies = []

    for i in global_data_detect:  # line: time, id, dlc, data
        text = [i.time, i.id, i.length]
        if float(text[0]) > cnt + time_itv and len(idSet) > 0:
            FV[0] = len(idSet)  # num of distinct ID
            FV[3] = (47 + FV[2] * 8) * FV[1] / 500000  # BW = (47b + DLC * 8b) * num of msg / 500Kbps

            cs = cos_sim(FV)  # calculate cos similarity
            if cs < minCS or cs > maxCS:
                anomalies.append([int(cnt / time_itv), [initTime, text[0]], cs])

            # reset
            cnt += time_itv
            FV = [0, 0, 0, 0]
            idSet = [text[1]]
            initTime = ''
            FV[1] += 1
            FV[2] += int(text[2])
        else:
            if text[1] not in idSet:
                idSet.append(text[1])
                if len(idSet) == 1:
                    initTime = text[0]
            FV[1] += 1
            FV[2] += int(text[2])

    return anomalies  # html中通过 {{ dano.0 }} 调用此变量


def detect_seq_lstm(alphabet, letterRaw):
    model = load_model("../vehicle/LSTMModel/model/")
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
