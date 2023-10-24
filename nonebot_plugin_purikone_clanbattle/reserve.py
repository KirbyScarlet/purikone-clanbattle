# 预约

import nonebot

from nonebot import on_shell_command
from nonebot.rule import ArgumentParser

from nonebot.adapters import Bot, Event
from nonebot.params import ShellCommandArgs

try:
    from nonebot.adapters.onebot.v11 import Event as Eventv11
    from nonebot.adapters.onebot.v11 import MessageSegment as MessageSegmentv11
except ImportError:
    Eventv11 = None
    MessageSegmentv11 = None

from argparse import Namespace

from .utils import check_bot

reservation_args = ArgumentParser()
reservation_args.add_argument("n", type=int, choices=range(6), nargs="?", help="查看具体某王的预约表")
reservation = on_shell_command("预约表", parser=reservation_args, rule=check_bot)

reserve_args = ArgumentParser()
reserve_args.add_argument("n", type=str, help="预约表几面或几王")
reserve_args.add_argument("extra", type=str, nargs="?", choices=("b", "补"), help="是否预约补偿刀")

reserve = on_shell_command("预约", parser=reserve_args, rule=check_bot)

RESERVATION_HELP = """\
预约表 [几王]
例：
> 预约表
## 查看当前所有预约
> 预约表 e4
## 预约表 43-4"""

RESERVE_HELP = """\
预约 几王 [补] | [撤销] | [清除]
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
## 撤销某个预约
> 预约 清理
## 仅管理 清空当前预约表"""

async def check_reservation(args) -> str:
    """
    查询当前的预约表
    """
    pass

@reservation.handle()
async def _reservation(bot: Bot, event: Event, args: Namespace = ShellCommandArgs()):
    await reservation.finish("#预约表\n"+str(args))
    if isinstance(event, Eventv11):
        pass

@reserve.handle()
async def _reserve(bot: Bot, event: Event, args: Namespace = ShellCommandArgs()):
    await reserve.finish("#预约\n"+str(args))