import pandas as pd
import threading
import multiprocessing
import time
hex2bin_map = {
   "0":"0000",
   "1":"0001",
   "2":"0010",
   "3":"0011",
   "4":"0100",
   "5":"0101",
   "6":"0110",
   "7":"0111",
   "8":"1000",
   "9":"1001",
   "A":"1010",
   "B":"1011",
   "C":"1100",
   "D":"1101",
   "E":"1110",
   "F":"1111",
}

bin2hex_map = {
   "0000":"0",
   "0001":"1",
   "0010":"2",
   "0011":"3",
   "0100":"4",
   "0101":"5",
   "0110":"6",
   "0111":"7",
   "1000":"8",
   "1001":"9",
   "1010":"A",
   "1011":"B",
   "1100":"C",
   "1101":"D",
   "1110":"E",
   "1111":"F"
}
def hex_str_to_binary_str(hex_str):
    tmp = ""
    for i in hex_str:
        tmp = tmp + hex2bin_map[i]
    return tmp
def binary_str_to_hex_str(binary_str):
    tmp = ""
    ll = len(binary_str)
    # 这样写为什么不会报bug呢？
    for i in range(0, ll, 4):
        # 应当是不会下标越界的
        tmp = tmp + bin2hex_map[binary_str[i:i+4]]
    return tmp

class CAN_DATA:
    type_name = None
    subnet = None  # subnet is somehow not necessary
    df = pd.DataFrame()

# 调用格式：cutting_data_into_standard_style(Logging0, asc)  默认寻找目录是在source文件夹下面的
# 这个函数是处理实车数据的，谨记之
def cutting_data_into_standard_style(file_name, file_type, output_file_name):  #速度基准，处理12mb数据，大约需要7-8分钟
    f = open('./src/' + file_name + '.' + file_type, 'r')

    TIME_POS = 1
    DLC_POS = 6
    DATA_POS = 7
    CANID_POS = 3
    SUBNET_POS = 2
    CAN_FLAG = "Length"

    TIME_POS_IN_CANFD = 1
    DLC_POS_IN_CANFD = 9
    DATA_POS_IN_CANFD = 10
    CANID_POS_IN_CANFD = 5
    SUBNET_POS_IN_CANFD = 3
    CANFD_FLAG = "CANFD"

    time_plus = None
    type_name = None
    can_id = None
    subnet = None
    data = None
    data_length = None

    val = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    # 在这里，我们希望用CANFD以及CAN以及子网编号用于区分，从而进行合理的操作
    # 需要重构一个数据结构出来，感觉是比较复杂的

    data_frame_list = pd.DataFrame(columns = ['time', 'can_id', 'length', 'data0', 'data1', 'data2', 'data3', 'data4',
                                              'data5', 'data6', 'data7', 'data_in_binary', 'data_in_hex', 'anormal', 'subnet',
                                              'type_name'])

    '''
    df_single = pd.DataFrame([{'time': time, 'can_id': can_id, 'length': data_length, 'data0': data[0],
                               'data1': data[1], 'data2': data[2], 'data3': data[3],
                               'data4': data[4], 'data5': data[5], 'data6': data[6], 'data7': data[7],
                               'data_in_binary': hex_str_to_binary_str(data), 'data_in_hex': data,
                               'anormal': 0, 'subnet': subnet, 'type_name': type_name}])
    '''

    times = 0
    for line in f:

        origin_data = line.split()
        # 尽可能优化速度
        if(len(origin_data) == 0 or origin_data[0][0] not in val):
            continue
        if(len(origin_data) <= 14): continue
        # print(origin_data)

        # 也就是说，数据还是要输出的？
        # print(origin_data)
        # 尽可能的在降低时间复杂度了 看起来速度还可以的哦
        if origin_data[14] == 'Length':
            data_length = int(origin_data[DLC_POS-1], 10) # 数据字段的长度
            if data_length > 8:
                continue
            time_plus = origin_data[TIME_POS-1]
            type_name = "CAN" # 不再区分CAN和CANFD
            can_id = origin_data[CANID_POS-1]
            subnet = origin_data[SUBNET_POS-1]
            
            data = origin_data[DATA_POS-1]
            for i in range(1, data_length):
                data = data + origin_data[DATA_POS-1+i]
            # print(data)
        # CANFD也还是存进去吧，子网号也存进去的

        elif origin_data[1] == 'CANFD':
            time_plus = origin_data[TIME_POS_IN_CANFD - 1]
            type_name = "CANFD"
            can_id = origin_data[CANID_POS_IN_CANFD - 1]
            subnet = origin_data[SUBNET_POS_IN_CANFD - 1]
            data_length = int(origin_data[DLC_POS_IN_CANFD - 1], 10)  # 数据字段的长度
            if data_length > 8:
                continue

            data = origin_data[DATA_POS_IN_CANFD - 1]
            # 这里的data实际上是16进制
            for i in range(1, data_length):
                data = data + origin_data[DATA_POS_IN_CANFD - 1 + i]
            # print(data)
        else:
            continue
        data = data.upper()
        '''
        df_single = pd.DataFrame([{'time':time, 'can_id':can_id,'length':data_length, 'data0': data[0:2], 'data1':data[2:4], 'data2':data[4:6], 'data3':data[6:8],
                     'data4':data[8:10], 'data5':data[10:12], 'data6':data[12:14], 'data7':data[14:16], 'data_in_binary':hex_str_to_binary_str(data), 'data_in_hex':data,
                     'anormal':0, 'subnet':subnet, 'type_name':type_name}])
        # 看一看一万条数据要处理多久
        
        data_frame_list = data_frame_list.append(df_single, ignore_index=True)
        '''
        tmp_arr_list = [time_plus, can_id, data_length, data[0:2], data[2:4], data[4:6], data[6:8], data[8:10],
                                    data[10:12], data[12:14], data[14:16], hex_str_to_binary_str(data),
                                    data, 0, subnet, type_name]
        # 这里的times记得++，防止append出现无法预知的错误

        data_frame_list.loc[times] = tmp_arr_list
        # print(data_frame_list)
        times = times + 1
        if times % 5000 == 0:
            print(times)
            another_list = pd.read_csv('./src/' + output_file_name, index_col = 0)
            data_frame_list = another_list.append(data_frame_list)
            data_frame_list.to_csv('./src/' + output_file_name)
            data_frame_list = None
            data_frame_list = pd.DataFrame(columns = ['time', 'can_id', 'length', 'data0', 'data1', 'data2', 'data3', 'data4',
                                              'data5', 'data6', 'data7', 'data_in_binary', 'data_in_hex', 'anormal', 'subnet',
                                              'type_name'])
            localtime = time.asctime(time.localtime(time.time()))
            print("本地时间为 :", localtime)
            # 本来就应该采取边读边写的策略，提高效率
    f.close()
    # 边读边写，提高运行效率efficiency

# 这个函数是处理通信矩阵数据的
def exchange_data(target_path, res_path):
    time_plus = None
    type_name = None
    can_id = None
    subnet = None
    data = None
    data_length = None
    res_path = './src_of_real_data/' + res_path
    target_path = './src_of_real_data/' + target_path
    df1 = pd.read_csv(target_path, index_col = 0)
    data_frame_list = pd.DataFrame(columns=['time', 'can_id', 'length', 'data0', 'data1', 'data2', 'data3', 'data4',
                                            'data5', 'data6', 'data7', 'data_in_binary', 'data_in_hex', 'anormal',
                                            'subnet',
                                            'type_name'])
    times = 0

    for i in range(0, df1.shape[0]):
        # 下面对数据进行循环处理，在这里展现了分层处理的合理性
        # 想要完成数据处理process，我们是一定需要information的
        time_plus = df1.iloc[i]['Abs Time(Sec)']
        type_name = "CAN"
        subnet = df1.iloc[i]['Network']
        can_id = df1.iloc[i]['PT']
        data_length = 8
        data = ""
        for love in range(1, 9):
            tmp = df1.iloc[i]['B' + str(love)]
            if pd.isnull(tmp):
                tmp = "00"
            tmp = str(tmp)
            if(len(tmp) == 1): tmp = "0" + tmp;
            data = data + tmp

        tmp_arr_list = [time_plus, can_id, data_length, data[0:2], data[2:4], data[4:6], data[6:8], data[8:10],
                        data[10:12], data[12:14], data[14:16], hex_str_to_binary_str(data),
                        data, 0, subnet, type_name]

        # 这里使用了索引
        # 我看每处理5000条要多久呢？暂时是不太清楚的
        data_frame_list.loc[times] = tmp_arr_list
        times = times + 1
        if times % 5000 == 0:
            print(times)
            another_list = pd.read_csv(res_path, index_col = 0)
            data_frame_list = another_list.append(data_frame_list)
            data_frame_list.to_csv(res_path)
            data_frame_list = None
            data_frame_list = pd.DataFrame(columns = ['time', 'can_id', 'length', 'data0', 'data1', 'data2', 'data3', 'data4',
                                              'data5', 'data6', 'data7', 'data_in_binary', 'data_in_hex', 'anormal', 'subnet',
                                              'type_name'])
            localtime = time.asctime(time.localtime(time.time()))
            print("本地时间为 :", localtime)

if __name__ == '__main__':
    # cutting_data_into_standard_style("Logging", "asc")

    # 开四个进程跑，速度还是不错的哦
    '''
    t_cut1 = multiprocessing.Process(target=cutting_data_into_standard_style, args=("{LoggingBlock1}", "asc", "test1.csv"))
    t_cut2 = multiprocessing.Process(target=cutting_data_into_standard_style, args=("{LoggingBlock2}", "asc", "test2.csv"))
    t_cut3 = multiprocessing.Process(target=cutting_data_into_standard_style, args=("{LoggingBlock3}", "asc", "test3.csv"))
    t_cut4 = multiprocessing.Process(target=cutting_data_into_standard_style, args=("{LoggingBlock4}", "asc", "test4.csv"))
    # cutting_data_into_standard_style("{LoggingBlock1}", "asc", "test1.csv")

    t_cut1.start()
    t_cut2.start()
    t_cut3.start()
    t_cut4.start()
    
    # 这里开多进程，可以极大程度上提高运行的速度 speed的
    '''
    t_cut1 = multiprocessing.Process(target=exchange_data,
                                     args=("target1.csv", "target1_res.csv"))
    t_cut2 = multiprocessing.Process(target=exchange_data,
                                     args=("target2.csv", "target2_res.csv"))
    t_cut3 = multiprocessing.Process(target=exchange_data,
                                     args=("target3.csv", "target3_res.csv"))
    t_cut4 = multiprocessing.Process(target=exchange_data,
                                     args=("target4.csv", "target4_res.csv"))
    # cutting_data_into_standard_style("{LoggingBlock1}", "asc", "test1.csv")
    # 给我跑起来哦，多进程

    t_cut1.start()
    t_cut2.start()
    t_cut3.start()
    t_cut4.start()



