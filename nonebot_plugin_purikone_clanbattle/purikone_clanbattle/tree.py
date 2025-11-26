## 挂树

from nonebot.adapters import Message
from argparse import Namespace

from .utils.sqliteapi import (
    get_currenthp,
    get_maxhp,
    get_chapter,
    on_tree,
    climb_tree,
    get_status,
    get_turn,
    fell_tree,
    start_challenge
)

async def tree(group_id: str, user_id: str, msg: str):
    res = []
    # 检查刀手是否申请出刀
    _t, _b, _c, _n = await on_tree(group_id, user_id)
    if not _b:
        res.append({"text": "您未申请出刀，已自动申请。\n"})
        await start_challenge(group_id, user_id, _b, False, "")
    if _t:
        return [{"text": "你已经在树上。"}]
    await climb_tree(group_id, user_id, msg)
    res.append({"text": f"已挂树\n"})
    # 查当前的树
    turn = await get_turn(group_id, _b)
    maxhp = await get_maxhp(turn, _b)
    currenthp = await get_currenthp(group_id, _b)
    res.append({"text": f"【{turn}-{_b}】: {currenthp} / {maxhp}\n"})
    _s = await get_status(group_id, _b)
    for user, tree, _, notes in _s:
        res.append({"at": f"{user}"})
        res.append({"text": f"{'已挂树' if tree else '正在挑战'} {notes}\n"})
    return res

async def christmas_tree(group_id: str, user_id: str):
    # 取消挂树
    _t, _b, _c, _n = await on_tree(group_id, user_id)
    if not _b:
        return [{"text": "您没有挂树，甚至没申请出刀"}]
    if not _t:
        return [{"text": "您没有挂树"}]
    await fell_tree(group_id, user_id)
    return [{"text": "取消挂树成功"}]

