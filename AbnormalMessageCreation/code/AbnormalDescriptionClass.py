

# 这个类用于输出需要的异常信息
class AbnormalDescriptionClass:

    # 现在暂时先确定四种不同类型的攻击
    dictAttackStrToNum = {"insert attack":1, "erase attack":2, "reput attack":3, "changedatafield attack":4}
    attackType = None
    attackCanId = None
    attackTimeRange = None
    # 攻击的具体内容，这个应当如何输出日志呢？暂时是不清楚的
    # 这种代码没有持久化操作，显然是不舒服的
    attackDescription = None
    # 如何定义消息日志呢？这个是输出攻击具体消息的日志
    def writeIntoTxt(self):
        return None