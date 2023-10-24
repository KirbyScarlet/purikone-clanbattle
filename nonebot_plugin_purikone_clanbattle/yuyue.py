#

import nonebot

from nonebot import on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.adapters.onebot.v11 import MessageSegment

reservation_args = ArgumentParser()
reservation_args.add_argument("n", type=str, default="0", dest=n, help="预约表几面或几王")
reservation = on_shell_command("预约表", parser=reservation_args)

reserve_args = ArgumentParser()
reserve_args.add_argument("n", dest="n", help="预约表几面或几王")
reserve_args.add_argument("b", "补", action="store_true", dest="", help="是否预约补偿刀")
reserve_args.add_argument("撤销", action="store_true", dest="cancel", help="预约表几刀")
reserve = on_shell_command("预约", parser=reserve_args)

RESERVATION_HELP = """\
预约表 [几王]
例：
> 预约表
## 查看当前所有预约
> 预约表 e4
## 预约表 43-4"""

RESERVE_HELP = """\
预约 [几王] [补] | [撤销]
例：
> 预约 3
## 预约下一个3王
> 预约 e3
## 预约下一个e3，若当前为d3，则e3前不提醒
> 预约 43-3
## 精确预约某一圈3王，若错过，则提醒后取消此次预约
> 预约 e4 补
## 预约补偿
> 预约 撤销
## 撤销全部预约
> 预约 撤销 e5
## 撤销某个预约"""

