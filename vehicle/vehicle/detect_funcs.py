# 存放用以检测数据的函数，返回报错信息
from .parse_funcs import cos_sim


def detect_seq_id_statistics(id_list, idFinalStat):
    idAppear = {}  # ID: prev, curr
    totalLength = len(id_list)
    uniqueIDs = idFinalStat.keys()

    anomalies = []

    for i in range(totalLength):
        tmpID = id_list[i]
        if tmpID not in uniqueIDs:
            anomalies.append('Anomaly detected: ID ' + tmpID + ' unidentified\n')
            continue
        elif tmpID not in idAppear.keys():
            idAppear[tmpID] = [i, i]
        else:
            prev = idAppear[tmpID][1]
            curr = i
            idAppear[tmpID] = [prev, curr]
            if curr - prev < idFinalStat[tmpID][2] or curr - prev > idFinalStat[tmpID][3]:
                anomalies.append('Anomaly detected: ID ' + tmpID + ' with unusual intervals:' + str(curr - prev) + '\n')
    return anomalies


def detect_seq_id_survival_rate(id_list, SRDict):
    idChunk = {}  # {ID: probability in a chunk, ...}
    length = len(id_list)
    chunk = 100
    sig = 1 / chunk  # probability of one occurrence
    pos = 0  # global position
    chunkPos = 0  # position in a chunk

    anomalies = []

    while pos < length:
        ID = id_list[pos]
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
                    anomalies.append('Anomaly detected: ID ' + ID + ' with frequency ' +
                                     str(round(prob, 2)) + '\n')
            idChunk.clear()
        pos += 1
        chunkPos = (chunkPos + 1) % chunk
    return anomalies


def detect_seq_cos_sim(global_data_detect, CSlist):
    FV = [0, 0, 0, 0]  # num of distinct ID, num of msg, dlc Sum, Band Width
    idSet = []
    cnt = 0
    time_itv = 0.01
    minCS = min(CSlist)
    maxCS = max(CSlist)

    anomalies = []

    for i in global_data_detect:  # line: time, id, dlc, data
        text = [i.time, i.id, i.length]
        if float(text[0]) > cnt + time_itv and len(idSet) > 0:
            FV[0] = len(idSet)  # num of distinct ID
            FV[3] = (47 + FV[2] * 8) * FV[1] / 500000  # BW = (47b + DLC * 8b) * num of msg / 500Kbps

            cs = cos_sim(FV)  # calculate cos similarity
            if cs < minCS or cs > maxCS:
                anomalies.append('Anomaly detected: ID sub seq ' + str(int(cnt / time_itv)) +
                                 ' with unusual cosine sim: ' + str(cs) + '\n')

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

    return anomalies
