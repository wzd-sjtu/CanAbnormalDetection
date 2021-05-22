# 用以存放解析数据的函数
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
