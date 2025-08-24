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
    history_today,
    get_reserve,
)

async def status(group_id: str):
    res = []
    for i in range(1,6):
        turn = await get_turn(group_id, i)
        maxhp = await get_maxhp(turn, i)
        currenthp = await get_currenthp(group_id, i)
        res.append({"text": f"【{turn}-{i}】: {currenthp} / {maxhp}\n"})
        _tree = await get_status(group_id, i)
        _hedao = await get_reserve(group_id, i)
        for t in _tree:
            if t[1] == 1:
                res.append({"at": t[0]})
                res.append({"text": f" 已挂树 {"补偿刀 " if t[2] else ""}{t[3]}\n"})
            else:
                res.append({"at": t[0]})
                res.append({"text": f" 正在挑战 {"补偿刀 " if t[2] else ""}{t[3]}\n"})
        for h in _hedao:
            if turn==h[2]:
                res.append({"at": h[1]})
                res.append({"text": f" 可合刀\n"})
    a, f, e, c = await history_today(group_id)
    title = {"text": f"今日报刀总数：{a}\n整刀数：{f} 尾刀数：{c} 未补刀：{e-c}\n"}
    res.insert(0, title)
    
    #预约表
    reserve = await get_reserve(group_id)
    if reserve:
        res.append({"text": "==========\n预约表:\n"})
        reserve.sort(key=lambda x: x[3])
        for _, user, turn, bossid, notes in reserve:
            currentturn = await get_turn(group_id, bossid)
            if turn == 0:
                res.append({"at": user})
                res.append({"text": f"【{currentturn+1}-{bossid}】 {notes}\n"})
            else:
                res.append({"at": user})
                res.append({"text": f"【{turn}-{bossid}】{notes}\n"})

    return res

    