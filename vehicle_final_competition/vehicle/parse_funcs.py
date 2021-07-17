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
    id_raw_stat = {}        # id: numbers, first, last, prev, min_interval, max_interval
    id_weight_stat = {}     # id: mu, sigma, max_interval
    line_No = 2

    itv_list = {}
    length = len(id_list)

    for i in id_list:
        if i not in id_raw_stat.keys():
            id_raw_stat[i] = [1, line_No, line_No, line_No, length, 0]
            itv_list[i] = []
        else:
            tmp = id_raw_stat[i]
            id_raw_stat[i][0] += 1
            id_raw_stat[i][2] = line_No  # currNo
            itv_list[i].append(line_No - tmp[3])
            if (line_No - tmp[3]) < tmp[4]:
                id_raw_stat[i][4] = line_No - tmp[3]
            if (line_No - tmp[3]) > tmp[5]:
                id_raw_stat[i][5] = line_No - tmp[3]
            id_raw_stat[i][3] = line_No
        line_No += 1

    for i, j in itv_list.items():
        mu = float(numpy.mean(j))
        sigma = float(numpy.std(j))
        id_weight_stat[i] = [round(mu, 4), round(sigma, 4), id_raw_stat[i][5]]

    return id_weight_stat


def seq_id_survival_rate(id_list, id_weight_stat):
    """ 计算id序列的生存率，
        返回id生存率的最小和最大值字典 """

    max_itv_list = [j[2] for j in id_weight_stat.values()]
    max_itv = max(max_itv_list)

    total_len = len(id_list)
    id_set = set(id_list)
    chunk_len = max_itv  # size of id_seq chunk
    SR_dict = {}  # id : [min SR, max SR], ... , 'chunk_len': chunk_len
    pos = 0

    while pos + chunk_len < total_len:
        # if the last chunk is shorter than chunkLen
        # attach it to the previous one
        if pos + chunk_len * 2 < total_len:
            id_chunk = id_list[pos:pos + chunk_len]
        else:
            id_chunk = id_list[pos:-1]

        # update the minSR & maxSR in the chunk for every unique ID in idSeq
        for i in id_set:
            rate = id_chunk.count(i)
            if i not in SR_dict.keys():
                SR_dict[i] = [rate, rate]
            else:
                SR_dict[i] = [min(SR_dict[i][0], rate), max(SR_dict[i][1], rate)]

        pos += chunk_len

    # for i in SR_dict.values():
    #     i[0] = round(i[0], 4)
    #     i[1] = round(i[1], 4)

    SR_dict['chunk_len'] = chunk_len

    return SR_dict


def correlation(FV):
    UV = [4, 3, 2, 1]
    E_fv = numpy.mean(FV)
    E_uv = numpy.mean(UV)
    std_fv = numpy.std(FV)
    std_uv = numpy.std(UV)
    length = len(FV)

    cov = 0
    for i in range(length):
        cov += (FV[i] - E_fv) * (UV[i] - E_uv)
    cov /= length
    cor = cov / (std_fv * std_uv)
    return cor


def parse_seq_correlation(global_data, global_IDs):
    """ 计算id序列分块后，每块的余弦相似度，
        返回余弦相似度的列表 """
    cor_list = []  # final result, stores cos-sim of every sub-seqs
    FV = [0, 0, 0, 0]  # [num of msg, num of unique ID, num of single ID, mean of ID value]
    id_set = []  # stores every unique ID in a sub-seq
    single_id = []  # stores every ID that occurs only once in a sub-seq

    occur_times = {}  # {ID: times of occurrence, ...}
    s = set(global_IDs)
    for i in s:
        occur_times[i] = 0

    curr_time = float(global_data[0].time)
    time_itv = 0.1

    for msg in global_data:  # msg: [timestamp ,ID]
        # if a sub-sequence ends, calculate its cos similarity
        if float(msg.time) > curr_time + time_itv and FV[0] != 0:
            FV[1] = len(id_set)             # number of unique IDs
            FV[2] = len(single_id) * 10     # number of IDs that occurred only once
            FV[3] = FV[3] / FV[0] / 10      # the average of ID values

            # calculate
            cor = correlation(FV)
            cor_list.append(cor)

            # reset
            curr_time += time_itv
            FV = [0, 0, 0, 0]
            single_id = [msg.id]
            id_set = [msg.id]
            FV[0] += 1  # number of all messages

        # continue scanning for sub-sequence
        else:
            # the first occurrence of an ID in the sub-seq
            if msg.id not in single_id and occur_times[msg.id] == 0:
                single_id.append(msg.id)
                occur_times[msg.id] = 1
            # the repeated occurrence of an ID
            if msg.id in single_id:
                single_id.remove(msg.id)
                occur_times[msg.id] += 1
            # the first occurrence of a unique ID
            if msg.id not in id_set:
                id_set.append(msg.id)

            FV[0] += 1

            if "E+" in msg.id:
                tmp_id = msg.id[0] + msg.id[4] + msg.id[7]
            else:
                tmp_id = msg.id
            FV[3] += int(tmp_id, 16)

    return [min(cor_list), max(cor_list)]


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