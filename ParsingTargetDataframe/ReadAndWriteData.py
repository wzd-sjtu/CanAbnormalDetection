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

    time = None
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
            time = origin_data[TIME_POS-1]
            type_name = "CAN" # 不再区分CAN和CANFD
            can_id = origin_data[CANID_POS-1]
            subnet = origin_data[SUBNET_POS-1]
            
            data = origin_data[DATA_POS-1]
            for i in range(1, data_length):
                data = data + origin_data[DATA_POS-1+i]
            # print(data)
        # CANFD也还是存进去吧，子网号也存进去的

        elif origin_data[1] == 'CANFD':
            time = origin_data[TIME_POS_IN_CANFD - 1]
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
        tmp_arr_list = [time, can_id, data_length, data[0:2], data[2:4], data[4:6], data[6:8], data[8:10],
                                    data[10:12], data[12:14], data[14:16], hex_str_to_binary_str(data),
                                    data, 0, subnet, type_name]
        # 这里的times记得++，防止append出现无法预知的错误
        data_frame_list.loc[times] = tmp_arr_list
        times = times + 1
        if times % 3000 == 0:
            print(times)
            break
        # 还是开多线程处理程序吧，提高效率？
#for data_frame in data_frame_list:
 #   print(data_frame.type_name)
    #  print(data_frame.subnet)
    # print(data_frame.df)
# 在某种程度上，效率是可以接受的
    f.close()

    # 存储内容信息
    # 需要将这里的函数重写

    data_frame_list.to_csv('./src/' + output_file_name)


if __name__ == '__main__':
    # cutting_data_into_standard_style("Logging", "asc")

    # 开四个进程跑，速度还是不错的哦
    t_cut1 = multiprocessing.Process(target=cutting_data_into_standard_style, args=("{LoggingBlock1}", "asc", "test1.csv"))
    t_cut2 = multiprocessing.Process(target=cutting_data_into_standard_style, args=("{LoggingBlock2}", "asc", "test2.csv"))
    t_cut3 = multiprocessing.Process(target=cutting_data_into_standard_style, args=("{LoggingBlock3}", "asc", "test3.csv"))
    t_cut4 = multiprocessing.Process(target=cutting_data_into_standard_style, args=("{LoggingBlock4}", "asc", "test4.csv"))
    # cutting_data_into_standard_style("{LoggingBlock1}", "asc", "test1.csv")
    # 给我跑起来哦，多进程
    t_cut1.start()
    t_cut2.start()
    t_cut3.start()
    t_cut4.start()

