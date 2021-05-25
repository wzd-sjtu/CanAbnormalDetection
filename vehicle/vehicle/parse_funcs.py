from typing import Pattern
import numpy

import pandas as pd

from pandas import DataFrame

from keras.models import Sequential

from keras.layers import Dense

from keras.layers import LSTM

from keras.utils import np_utils

from keras.preprocessing.sequence import pad_sequences


def seq_id_statistics(id_list):
    """ 计算id序列的基本能统计特征：出现次数、平均周期、周期上下限，
        返回id的上述特征的字典 """
    # unique id: numbers, first, last, prev, min_interval, max_interval
    idRawStat = {}
    idFinalStat = {}  # unique id: numbers, avg_interval, min, max
    lineNo = 2
    length = len(id_list)

    for i in id_list:
        if i not in idRawStat.keys():
            idRawStat[i] = [1, lineNo, lineNo, lineNo, length, 0]
        else:
            tmp = idRawStat[i]
            idRawStat[i][0] += 1
            idRawStat[i][2] = lineNo  # currNo
            if (lineNo - tmp[3]) < tmp[4]:
                idRawStat[i][4] = lineNo - tmp[3]
            if (lineNo - tmp[3]) > tmp[5]:
                idRawStat[i][5] = lineNo - tmp[3]
            idRawStat[i][3] = lineNo
        lineNo += 1

    for ID, info in idRawStat.items():
        # (last occurrence - first occurrence) / (number-1)
        if info[0] != 1:
            avg_interval = (info[2] - info[1]) / (info[0] - 1)
            idFinalStat[ID] = [info[0], round(avg_interval, 2), info[4], info[5]]
        else:
            idFinalStat[ID] = [1, 0, 0, 0]

    return idFinalStat


def seq_id_survival_rate(id_list):
    """ 计算id序列的生存率，
        返回id生存率的最小和最大值字典 """
    totalLen = len(id_list)
    idSet = set(id_list)
    SRDict = {}  # id : [min SR, max SR],
    chunkLen = 100  # size of id_seq chunk
    pos = 0

    while pos + chunkLen - 1 < totalLen:
        # if the last chunk is shorter than chunkLen
        # attach it to the previous one
        if pos + chunkLen * 2 - 1 < totalLen:
            idChunk = id_list[pos:pos + chunkLen]
        else:
            idChunk = id_list[pos:-1]

        # update the minSR & maxSR in the chunk for every unique ID in idSeq
        for i in idSet:
            rate = idChunk.count(i) / chunkLen
            if i not in SRDict.keys():
                SRDict[i] = [rate, rate]
            else:
                SRDict[i] = [min(SRDict[i][0], rate), max(SRDict[i][1], rate)]

        pos += chunkLen

    return SRDict


def cos_sim(FV):
    """ 计算给定特征向量和单位向量之间的余弦相似度 """
    UV = [1, 1, 1, 1]
    dotpro = 0
    mod1 = 0
    mod2 = 0
    for i in range(4):
        dotpro += FV[i] * UV[i]
        mod1 += FV[i] ** 2
        mod2 += UV[i] ** 2
    mod1 = mod1 ** 0.5
    mod2 = mod2 ** 0.5
    return dotpro / (mod1 * mod2)


def parse_seq_cos_sim(global_data):
    """ 计算id序列分块后，每块的余弦相似度，
        返回余弦相似度的列表 """
    CSlist = []
    FV = [0, 0, 0, 0]  # 不同的ID数, 消息总数, dlc之和, 带宽
    idSet = []
    cnt = 0
    time_itv = 0.01  # 每个分段的时间间隔
    for i in global_data:  # line: time, id, dlc, data
        text = [i.time, i.id, i.length]
        if float(text[0]) > cnt + time_itv and len(idSet) > 0:
            FV[0] = len(idSet)  # num of distinct ID
            FV[3] = (47 + FV[2] * 8) * FV[1] / 500000  # BW = (47b + DLC * 8b) * num of msg / 500Kbps
            CSlist.append(cos_sim(FV))  # calculate cos similarity
            # reset
            cnt += time_itv
            FV = [0, 0, 0, 0]
            idSet = [text[1]]
            FV[1] += 1
            FV[2] += int(text[2])
        else:
            if text[1] not in idSet:
                idSet.append(text[1])
            FV[1] += 1
            FV[2] += int(text[2])

    FV[0] = len(idSet)
    FV[3] = (47 + FV[2] * 8) * FV[1] / 500000
    CSlist.append(cos_sim(FV))
    minCS = min(CSlist)
    maxCS = max(CSlist)
    return [minCS, maxCS]


def set_detect_seq_lstm(alphabet):
    # define the raw dataset
    # filepath =r"C:\Users\plw\Desktop\target_res(1).csv"
    # testflight = pd.read_csv(filepath)
    # alphabet = testflight["y"]
    # anomalies = []

    # alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # create mapping of characters to integers (0-25) and the reverse
    char_to_int = dict((c, i) for i, c in enumerate(alphabet))
    int_to_char = dict((i, c) for i, c in enumerate(alphabet))
    # prepare the dataset of input to output pairs encoded as integers
    num_inputs = 1000
    max_len = 100
    dataX = []
    dataY = []
    for i in range(num_inputs):
        start = numpy.random.randint(len(alphabet) - 2)
        end = numpy.random.randint(start, min(start + max_len, len(alphabet) - 1))
        sequence_in = alphabet[start:end + 1]
        sequence_out = alphabet[end + 1]
        dataX.append([char_to_int[char] for char in sequence_in])
        dataY.append(char_to_int[sequence_out])
        print(sequence_in, '->', sequence_out)
    # convert list of lists to array and pad sequences if needed
    X = pad_sequences(dataX, maxlen=max_len, dtype='float32')
    # reshape X to be [samples, time steps, features]
    X = numpy.reshape(X, (X.shape[0], max_len, 1))
    # normalize
    X = X / float(len(alphabet))
    # one hot encode the output variable
    y = np_utils.to_categorical(dataY)
    # create and fit the model
    batch_size = 1
    model = Sequential()
    model.add(LSTM(32, input_shape=(X.shape[1], 1)))
    model.add(Dense(y.shape[1], activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(X, y, epochs=1, batch_size=batch_size, verbose=2)
    # summarize performance of the model
    scores = model.evaluate(X, y, verbose=0)
    PATH = "../vehicle/LSTMModel"
    model.save(PATH+'/model/')
    print("Model Accuracy: %.2f%%" % (scores[1] * 100))
    # demonstrate some model predictions
    return  '训练完成' # html中通过 {{ dano.0 }} 调用此变量