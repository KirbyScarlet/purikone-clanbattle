# 公主连结会战机器人

兼容qq官方的公主连结团队战机器人，极简功能

### 0. 叠甲

- 本项目基于nonebot2开发。使用本项目请遵守MIT协议。
- 不推荐、不建议、不支持商用行为。
- 该机器人不会收集任何个人隐私信息，仅记录账号信息作为出刀依据或记录管理员权限。
- 该机器人仅保留团队战功能，不会添加其他娱乐功能，如抽卡，竞技场工具等。
- 由于qq官方审核限制，本机器人不会制作后台页面，所有管理通过聊天指令完成。
- 开发者可能饿死，但绝不会变质。

### 1. 食用说明书

- 根据机器人适配器，可选命令前缀

- 会战开始/会战重置
- 设定昵称 （仅官方bot使用）
- 申请出刀
- 报刀
- 尾刀
- 合刀
- 挂树
- 修改
- 预约
- sl

### 2. 命令详解

本文档将采用以下命令格式：

`命令` `<必选参数>``[可选参数]`

`命令` `reg(命令参数的正则表达式格式)`

#### 2.1 `会战开始` `[服务器类型]`

本群组或频道开始进行会战结算

参数列表：
```
服务器类型 可选值：
  b  b服官服 （默认）
  t  省服
  r  日服
```

命令示例：
```
> 会战开始
#本群组开始响应机器人命令，并默认使用bili官服的首领数据。

> 会战开始 r
#使用日服首领数据。
```

##### 2.2 `会战重置`

重置本群组或频道的会战数据

##### 2.3 `设定昵称` `<昵称>`

设定本群组或频道的昵称，仅适用于在使用qq官方bot情况下启用本命令。解决官方bot无法使用@用户的问题。

重复执行该命令会覆盖之前设置的昵称。机器人仅收集前8位字符串

参数列表：
```
昵称：必填值 任意非空字符串
```

命令示例：
```
> 设定昵称 罗张三
#后续机器人回复消息涉及用户时，使用该昵称代替。
```

##### 2.4 `申请出刀` `<首领编号>` `[是否补偿]` `[额外文字信息]`

记录用户开始出刀，该记录会体现在状态表上。

本命令前缀可使用单字 `进` 代替 `申请出刀`。**使用单字前缀时，出现命令格式错误将不会触发机器人的命令错误提示。**

参数列表：
```
首领编号：必填值 
  数字1-5

是否补偿：可选值
  b
  补 
选填一种即可

额外文字信息：可选值
  任意非空字符串
```

命令示例：
```
> 申请出刀 1
#记录用户开始挑战1号首领。

> 申请出刀 2 补
#记录用户使用补偿刀挑战2号首领。

> 申请出刀 5 58秒大补
#记录用户挑战5号首领，并在状态栏上显示备注信息

> 进3b
#简写命令，记录用户使用补偿刀挑战3号首领。
```

##### 2.5 `报刀` `<[首领编号]>` `<伤害数值>` `[是否是补偿刀]`

记录用户出刀记录，并进行结算

参数列表：
```
首领编号：
  若申请出刀后报刀，该参数可不填，使用申请出刀时的首领编号参数。
  若未申请出刀，该参数必填，参数类型为数字1-5。
  若申请出刀后报刀填写了该参数，若编号参数不同，则使用当前报刀指定的首领编号进行报刀结算。

伤害数值：必填值
  reg(^[1-9][0-9]*k?w?e?$)
  符合中文习惯的数字记录方式，例：
  23000000 2300w 2.3kw 0.23e

是否是补偿刀：可选值
  b
  补
选填一种即可
```

命令示例：
```
> 报刀 1 230w b
#记录用户挑战1号首领，并使用补偿刀进行结算，结算伤害为2300000。

> 报刀 2 4000w 
#记录用户挑战2号首领，伤害为40000000。

> 进3
> 报刀 400w
#用户申请挑战3号首领，并造成4000000伤害。

> 报刀 5 0
#掉刀
```

##### 2.6 `尾刀` `<[首领编号]>` `[是否是补偿刀]`

记录用户出刀记录，并进行战斗胜利结算

参数列表：
```
首领编号：
  若申请出刀后报刀，该参数可不填，使用申请出刀时的首领编号参数。
  若未申请出刀，该参数必填，参数类型为数字1-5。
  若申请出刀后报刀填写了该参数，若编号参数不同，则使用当前报刀指定的首领编号进行报刀结算。

是否是补偿刀：可选值
  b
  补
选填一种即可
```

命令示例：
```
> 尾刀 2

> 进4
> 尾刀
```

##### 2.7 `合刀` `<生命值数字>` `<生命值数字>` `[生命值数字]`

合刀补偿计算器

参数列表：
```
接受2个或3个数字。
  若仅有两个数字，则分别以两个数字为首领剩余血量，计算 缺少的伤害 或 尾刀补时 或 可能存在的满补垫刀。
  若存在3个数字，则以最大数作为首领剩余血量，另外两个数字作为两刀伤害，并分别计算先后出刀的尾刀补时和可能存在的满补垫刀。
数字类型：
  reg(^[1-9][0-9]*k?w?e?$)
```

命令示例：
```
> 合刀 2000 2300
剩余血量2000，刀伤2300，补偿31.74秒，再垫1464满补
==========
剩余血量2300，刀伤2000，还差300
第二刀砍1834，刀伤2000吃满补
刀伤2000先出，第二刀超过1286可满补


> 合刀 2000 2300 2600
2000先出，2300返86.52秒，再垫64满补
2300先出，2000返96.50秒
```

##### 2.8 `修改` `[周目数]`-`<首领编号>`:`<[数值]>` ...

主动修改当前状态

参数列表：
```
周目数：
  当未指定数值时，该参数必填，用于修改当前首领的周目数，血量保持不变。
  当指定数值时，该参数选填，若此时未指定周目数，则使用当前周目数进行修改。

首领编号：必填
  数字 1-5

数值：
  当未指定周目数时，该参数必填，用于修改当前周目首领的生命值。
  当指定周目数时，该参数选填。
数字类型：
  reg(^[1-9][0-9]*k?w?e?$)
  100%   #仅支持100%作为最大生命值

#以上组成一个命令组合，该命令支持多个组合
```

命令示例：
```
> 修改 42-1
#修改1号首领的周目数为42，生命值保持不变。

> 修改 43-2:2000w
#修改2号首领的周目数为43，生命值修改为20000000。

> 修改 5:0
#修改5号首领的生命值为0

> 修改 43-4:0 42-3:100%
#同时修改
```

##### 2.9 `挂树` `[取消]` `[文字备注]`

在状态表中添加刀手的挂树记录

参数列表：
```
取消：固定值
  挂树取消

文字备注：选填
  备注文字
```

命令示例：
```
> 挂树
#添加挂树记录

> 挂树 取消
#取消挂树记录

> 挂树 2000w
#添加挂树记录并备注，此处备注的数字不会进入报刀合计，后续报刀仍需报数字
```

##### 2.10 `预约` `[取消]` `[周目数]|[阶段数]` `<首领编号>` 

预约要出刀的首领

参数列表：
```
周目数：可选参数
  可选值：[a-e]
  当指定周目数时，不可指定阶段数。预约下一个可能的跨阶段首领。

阶段数：可选参数
  数值类型
  当指定阶段数时，不可指定周目数。预约指定周目数编号的首领。

首领编号：必填
  必填值：[1-5]
```

命令示例：
```
> 预约 2
#预约下一个2号首领

> 预约 43-2
#预约43周目的2号首领

> 预约 e4
#若当前未处于e阶段，则进入e阶段时提示出刀。若已进入e阶段，等同于 `预约4`
```

##### 2.11 `sl` `[?]` `[取消]`

记录今天（游戏结算日）的saveload行为。

参数列表：
```
?：可选参数 固定值
  查询今天是否已记录sl

取消：可选参数 固定值
  取消今天sl记录
```

命令示例：
```
> sl
#记录sl

> sl ?
#查询今天是否已记录sl

> sl 取消
#取消今天的sl记录
```

### 3. 二次开发规范

本机器人的**会战核心功能**和**机器人调用**完全解耦，如果您使用了别的机器人框架，可非常轻易的直接接入核心功能，只需要在机器人框架中提供相应的群组信息和用户id以及处理好的命令参数即可。

**会战核心功能**默认使用sqlite3作为存储记录，如果您需要使用别的数据存储方式，也可以自行按规范定义存储相关api。

#### 3.1 会战命令api

`purikone_clanbattle.apply.apply(group_id: str, user_id: str, args: argparse.Namespace)`

申请出刀

`purikone_clanbattle.apply.cancel_apply(group_id: str, user_id: str)`

取消申请出刀

`purikone_clanbattle.create.create(group_id: str, user_id: str, args: argparse.Namespace)`

创建会战，开始会战

`purikone_clanbattle.hedao.hedao(a: int, b:int, c:int)`

合刀计算器

`purikone_clanbattle.modify.modify(group_id: str, args: argparse.Namespace)`

修改首领数据

`purikone_clanbattle.report.report(group_id: str, user_id: str, args: argparse.Namespace)`

报刀

`purikone_clanbattle.report.end_report(group_id: str, user_id: str, args: argparse.Namespace)`

尾刀报刀

`purikone_clanbattle.report.cancel_report(group_id: str, user_id: str)`

取消最近一次报刀

`purikone_clanbattle.reserve.reserve(group_id: str, user_id: str, args: argparse.Namespace)`

预约出刀

`purikone_clanbattle.reserve.cancel_reserve(group_id: str, user_id: str)`

取消预约出刀

`purikone_clanbattle.reserve.status(group_id: str, user_id: str)`

状态表

`purikone_clanbattle.saveload.saveload(group_id: str, user_id: str, args: argparse.Namespace)`

记录sl

`purikone_clanbattle.saveload.cancel_saveload(group_id: str, user_id: str)`

取消记录sl

`purikone_clanbattle.tree.tree(group_id: str, user_id: str, args: argparse.Namespace)`

挂树

`purikone_clanbattle.tree.christmas_tree(group_id: str, user_id: str)`

取消挂树

*`purikone_clanbattle.user.user_add(group_id: str, user_id: str, args: argparse.Namespace)`

仅qq官方bot使用，添加用户并记录昵称

*`purikone_clanbattle.user.user_exit(group_id: str, user_id: str)`

仅qq官方bot使用，删除用户

*`purikone_clanbattle.user.get_user_nickname(group_id: str, user_id: str)`

仅qq官方bot使用，获取用户昵称

#### 3.2 后端数据存储相关api

`purikone_clanbattle.utils.api.group_check(group_id: str)`

当前群组是否开启会战，
参数：群组id

`purikone_clanbattle.utils.api.group_set(group_id: str, server: str)`

开启会战，
参数：群组id，服务器类型["b","r","t"]

`purikone_clanbattle.utils.api.group_server(group_id: str)`

获取当前会战服务器类型，
参数：群组id

*`purikone_clanbattle.utils.api.add_group(group_id: str, user_id: str, nickname: str)`

仅qq官方bot使用，用户加入出刀人员列表。
参数：群组id，用户id，用户昵称

*`purikone_clanbattle.utils.api.exit_group(group_id: str, user_id: str)`

仅qq官方bot使用，用户退出出刀人员列表。
参数：群组id，用户id

*`purikone_clanbattle.utils.api.get_group_members(*, group_id: str = None, user_id: str = None) -> list[list[str, str]]`

仅qq官方bot使用，获取当前会战成员列表。
参数：群组id，用户id(可选)

`purikone_clanbattle.utils.api.on_tree(group_id: str, user_id: str) -> list[list[bool, int, bool, str]]`

检查刀手是否在挑战中，是否挂树。
参数：群组id，用户id
返回值：list[list[是否在树上, 首领编号, 该刀是否时补偿刀, 额外文字备注]]

`purikone_clanbattle.utils.api.clime_tree(group_id: str, user_id: str, notes: str = "")`

挂树
参数：群组id，用户id，额外文字备注

`purikone_clanbattle.utils.api.fell_tree(group_id: str, user_id: str)`

仅取消挂树
参数：群组id，用户id

`purikone_clanbattle.utils.api.get_status(group_id: str, boss_id: int = 0) -> list[list[str, bool, str]]`

查看当前已申请挑战刀手的出刀状态
参数：群组id，首领编号(可选)
返回值：list[list[用户id, 是否挂树, 额外文字信息]]
 
`purikone_clanbattle.utils.api.start_challenge(group_id: str, user_id: str, boss_id: str, compensiate: bool = False, notes: str = "")`

记录申请出刀
参数：群组id，用户id，首领编号，是否为补偿刀，额外文字备注

`purikone_clanbattle.utils.api.cancel_challenge(group_id: str, user_id: str = None, boss_id: int|str = None)`

取消申请出刀，从出刀列表中移除
参数：群组id，用户id(可选)，首领编号(可选)

`purikone_clanbattle.utils.api.boss_status(group_id: str, boss_id: int) -> bool`

查看当前首领是否可以被挑战
参数：群组id，首领编号
返回值：是否可以被挑战

`purikone_clanbattle.utils.api.compensiated(group_id: str, user_id: str) -> bool`

检查当前刀手是否持有补偿刀
参数：群组id，用户id
返回值：是否持有补偿刀

`purikone_clanbattle.utils.api.get_chapter(turn: int) -> Literal["a","b","c","d","e"]`

获取当前首领阶段
参数：当前周目数
返回值：当前阶段

`purikone_clanbattle.utils.api.get_turn(group_id: str, boss_id: int) -> int`

获取群组某个周目的首领所在的阶段
参数：群组id，首领编号
返回值：当前周目数

`purikone_clanbattle.utils.api.get_step(chapter: Literal["a","b","c","d","e"]) -> int | list[int]`

获取跨阶段的前一个周目
参数：某个阶段（可选）
返回值：list[阶段数]

`purikone_clanbattle.utils.api.get_maxhp(turn: int, boss_id: int) -> int`

获取某周目某首领的最大生命值
参数：周目数，首领编号
返回值：最大生命值

`purikone_clanbattle.utils.api.get_currenthp(group_id: str, boss_id: int) -> int`

获取某群组当前某首领的生命值
参数：群组id，首领编号
返回值：当前生命值

`purikone_clanbattle.utils.api.update_bosshp(gropu_id: str, boss_id: int, user_id: str, turn: int, hp: int)`

报刀伤害记录，更新当前首领生命值（采用新增记录的方式）
参数：群组id，首领编号，用户id，周目数，伤害值

`purikone_clanbattle.utils.api.update_history(group_id: str, boss_id: int, user_id: str, turn: int, damage: int, end: Literal[1,0], compensiate: Literal[1,0])`

报刀的历史记录，用于统计尾刀或补刀等
参数：群组id，首领编号，用户id，周目数，伤害值，是否是尾刀，是否使用了补偿刀

`purikone_clanbattle.utils.api.history_today(group_id: str) -> [int, int, int, int]`

获取群组今天已出的刀
参数：群组id
返回值：所有报刀的刀数，整刀数，尾刀数，补刀数

`purikone_clanbattle.utils.api.reserve_boss(group_id: str, boss_id: int, user_id: str, nickname: str = "", turn: int = 0, notes: str = "")`

添加预约表
参数：群组id，首领编号，用户id，用户昵称，周目数，备注

`purikone_clanbattle.utils.api.cancel_reserve(group_id: str, boss_id: int, user_id: str)`

取消预约
参数：群组id，首领编号，用户id

`purikone_clanbattle.utils.api.get_reserve(group_id: str, boss_id: int = 0) -> list[list[str, str, str, int, int, str]]`

获取预约表
参数：群组id，首领编号（可选）
返回值：list[list[群组id, 用户id, 昵称, 周目数, 首领编号, 备注]]

同步方法

`purikone_clanbattle.utils.api.get_today_start_time(server: Literal["b","j","t"]) -> int`

获得游戏结算日的起始时间戳，单位纳秒
参数：服务器地区，默认b服官服
返回值：时间戳(纳秒)
