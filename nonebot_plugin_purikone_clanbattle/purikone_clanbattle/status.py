# 查看当前状态

__all__ = ['status']

from argparse import Namespace
from nonebot.adapters import Message

from .utils.sqliteapi import (
    get_chapter,
    boss_status,
    get_maxhp,
    get_turn,
    get_status,
    get_currenthp,
    history_today
)

async def status(group_id: str):
    res = []
    for i in range(1,6):
        turn = await get_turn(group_id, i)
        maxhp = await get_maxhp(turn, i)
        currenthp = await get_currenthp(group_id, i)
        res.append({"text": f"【{turn}-{i}】: {currenthp} / {maxhp}\n"})
        _tree = await get_status(group_id, i)
        for t in _tree:
            if t[1] == 1:
                res.append({"at": t[0]})
                res.append({"text": f" 已挂树 {t[2]}\n"})
            else:
                res.append({"at": t[0]})
                res.append({"text": f" 正在挑战\n"})
    a, f, e, c = await history_today(group_id)
    title = {"text": f"今日报刀总数：{a}\n整刀数：{f} 尾刀数：{c} 未补刀：{e-c}\n"}
    res.insert(0, title)

    return res

    