# 最底层的数据单元
class SingleData:

    def __init__(self, can_id, time, data_in_hex, data_in_binary):
        self.can_id = can_id
        # 这里的time有点不太清楚
        self.time = time
        self.data_in_hex = data_in_hex
        self.data_in_binary = data_in_binary
