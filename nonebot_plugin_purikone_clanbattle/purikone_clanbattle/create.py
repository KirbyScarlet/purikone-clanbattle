# 创建会战&开始会战

from argparse import Namespace
from nonebot.adapters import Message
from .utils.sqliteapi import (
    group_check,
    group_set,
    group_reset
)

CREATE_HELP="""
命令格式：
  @机器人 会战开始 [B/J/T]
B 简中官服
J 日服
T 省服"""
RESTART_HELP = """
命令格式：
  @机器人 会战重置"""

async def create_parser(msg: Message):
    msg = msg.extract_plain_text()
    if msg in ["b", "B" , "简中", "B服"]:
        return Namespace(mode="B")
    elif msg in ["j", "J", "日服"]:
        return Namespace(mode="J")
    elif msg in ["t", "T", "省服", "台服"]:
        return Namespace(mode="T")
    elif msg == "":
        return Namespace(mode="B")
    else:
        return None
    
async def create(group_id: str, args: Namespace) -> list[dict]:
    res_text = []
    server, _ = await group_check(group_id)
    if server:
        res_text.append({"text": """\
本群已开启会战，请勿重复开启。
若要重置会战数据，请管理员执行以下命令：
@机器人 /会战重置"""})
    else:
        await group_set(group_id, args.mode)
        res_text.append({"text": """\
会战开始"""})
    return res_text

async def restart(group_id: str) -> bool:
    await group_reset(group_id)