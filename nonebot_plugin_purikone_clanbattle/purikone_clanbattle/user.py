# 加入会战

from argparse import Namespace
from nonebot.adapters import Message
from .utils.sqliteapi import (
    add_group,
    exit_group,
    get_group_members
)

async def user_parser(msg: Message):
    m = "".join(msg.extract_plain_text())
    if m:
        return Namespace(nickname=m)
    else:
        return Namespace(nickname=None)

async def user_add(group_id: str, user_id: str, args: Namespace):
    res = []
    c = await add_group(group_id, user_id, args.nickname[:8])
    if c:
        res.append({"text": f"昵称更新成功 {args.nickname[:8]}"})
    else:
        res.append({"text": f"加入成功 {args.nickname[:8]}"})
    return res

async def user_exit(group_id: str, user_id: str):
    await exit_group(group_id, user_id)

async def get_user_nickname(user_id: str):
    n = await get_group_members(user_id=user_id)
    if n:
        return [{"text": n}]
    else:
        return [{"text": "未加入行会"}]