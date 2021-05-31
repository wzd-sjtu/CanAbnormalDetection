异常报文构建类

友情提示：所有的id字典：
```
allCanIdList = ['19E', '621', '601', '348', '60C', '481', '263', '604',
                 '17D', '19D', '1.00E+09', '34A', '19B', '140', '52A',
                 '3D1', '191', '269', '4C9', 'C5', '4F1', '3.00E+09',
                 'C1', '3.00E+05', '4D1', '565', 'C9', '194', '141', '1F5',
                 '1.00E+05', '608', '120', '1C6', '471', '230', 'E1', '603',
                 '1C3', '4C1', '128', '589', '1F1', '12A']
```

# 1.数据格式
源数据来自100万条车载报文，按照时间间隔3s均等划分，划分出176个子数据，作为正常数据集。

攻击报文事实上源自对正常报文的修改，从而低成本模拟出攻击场景，也就是蕴含着异常报文的报文流。

数据使用dataframe存储，一共有16列，各个列意义鲜明，最重要的就是anormal列，代表着数据正常或者异常。

如果值为0，正常数据。如果不为0，代表的是生成的异常数据。

源数据的存储位置是 /src/HadCutData 文件夹下，如果想要改换攻击源数据，只需要替换文件即可。
```
time,can_id,length,
data0,data1,data2,data3,data4,data5,data6,data7,
data_in_binary,data_in_hex,anormal,subnet,type_name
```
# 2.攻击类型阐述
一共有四大类攻击，注入、删除、重放、数据域修改。

各个攻击的API使用方法已经写死，每次制造攻击以后，会生成一个攻击数据集，以及对应的描述。

生成的攻击数据集位置：\src\attack_test\attack_data.csv

对应的攻击描述文件位置：\src\attackDescription\myDescription.csv

在数据域攻击时，需要导入数据域字段规则，这个规则文件需要存放在此处：\src\learnedRule\result.csv

# 3.攻击API阐述

下面我们介绍各个攻击API的使用方法：

首先需要引入头文件，需要设置code文件夹为source文件夹。

引入代码：
```
from AbnormalCreateClass import AttackCreate
from LoadDataClass import LoadDataClass
from BasicClass import DataFieldAttackInformation

# 引入数据导入类，直接调用即可
loadDataExample = LoadDataClass()
loadDataExample.readHadCutData()

# 攻击制造类导入
attackCreateExample = AttackCreate()
attackCreateExample.sourceDataSnippet = loadDataExample.sourceDataSnippet
attackCreateExample.historyNormalDataSnippet = loadDataExample.historyNormalDataSnippet
```

之后就是攻击制造API了

## 1.注入攻击
注入攻击较为简单，需要提供的参数有can_id(str)，注入周期normal_T(s)，保留字段ratio=1，注入持续的时间exist_time(s)
```
# def insert_attack(self, id, normal_T, ratio, exist_time)
attackCreateExample.insert_attack('82', 0.01, 2,0.2)
```
调用后读取相应的文件即可获取内容。

## 2.删除攻击
删除攻击需要提供参数can_id(str)，持续时间exist_time(s)
```
# def erase_attack(self, id, exist_time):
attackCreateExample.erase_attack('82', 0.2)
```
调用后读取相应文件即可获取内容。

## 3.重放攻击
### 1.单id重放攻击
需要提供参数can_id(str)，持续时间exist_time(s)
```
# def reput_attack_SingleId(self, id, exist_time):
attackCreateExample.reput_attack_SingleId("82", 0.2)
```
### 2.全报文重放攻击
需要提供参数持续时间exist_time(s)
```
attackCreateExample.reput_attack_AllData(0.1)
```

## 4.数据域修改攻击
首先需要导入规则，这个在上文提到过。

当然，这里的规则导入已经写死了，只需要把规则放在目录下面即可。

接下来是数据域攻击的手段。

首先要选择数据域攻击大类型，有以下几种选择：

分别是随机攻击、定值/多值攻击、传感器攻击，具体字段存储在DataFieldAttackInformation类里面，当做一个静态变量使用。
```
randomAttack = 1
constOrMultivalueAttack = 2
sensorAttack = 3
# 选择了传感器类型攻击
valueAttackInfo.attackChoseType = valueAttackInfo.sensorAttack
```
倘若选择了传感器攻击，我们还要选取具体的攻击手段：
一共提供了四种类型攻击，分别是最大值、最小值、随机值、中间值（梯度不超过限度）
```
max_value_attack = 0
min_value_attack = 1
random_value_attack = 2
apt_advanced_value_attack = 3
# 选择了最大值攻击
valueAttackInfo.relatedThing = valueAttackInfo.max_value_attack
```

之后我们再给数据域攻击提供can_id(str)和持续时间exist_time(s)参数，并且把上面选择的攻击类型传入，
即可完成数据域攻击。

以下是一个简单的例子：
```

valueAttackInfo = DataFieldAttackInformation()
valueAttackInfo.attackChoseType = valueAttackInfo.sensorAttack
valueAttackInfo.relatedThing = valueAttackInfo.max_value_attack
attackCreateExample.change_data_field(valueAttackInfo, '17D', 0.2)

```

# 4.攻击类

如果想要生成大批量测试数据，直接使用API先制造，之后记得将attack_data.csv的数据复制到某个文件夹，即可完成数据制造。
