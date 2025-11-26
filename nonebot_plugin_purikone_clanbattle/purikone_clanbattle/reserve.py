# 预约表

from argparse import Namespace
from nonebot.adapters import Message
from .utils.sqliteapi import (
    reserve_boss,
    cancel_reserve,
    get_reserve,
    get_step,
    get_turn,
    get_currenthp,
)
import re

RESERVE_HELP = """\
命令格式：
  预约 首领编号
  预约 [合刀] 首领编号
  预约 [阶段] [周目] 首领编号
  预约 [取消] [周目] 首领编号
  预约表
注：
  预约当前周目首领时，将记录为【合刀请求】
  预约过号时，将保留预约记录，直到报刀时自动取消。
例：
  预约 4
    预约下一个4号首领
  预约 23-4
    预约23周目4号首领
  预约 d4
    预约d阶段第一个4号首领
  预约 取消
    取消当前所有预约
  预约 取消 4
    取消当前4号首领的预约"""

async def reserve_parser(msg: Message):
    n = msg.extract_plain_text().split()
    res = {
        "turn": 0,
        "bossid": 0,
        "note": "",
        "cancel": False
    }
    if "取消" in n:
        res["cancel"] = True
        return Namespace(**res)
    if "合刀" in n:
        res["turn"] = -1
        del n[0]
    m = n[0]
    note = "".join(n[1:])
    if m in "12345":
        res.update({"bossid":int(m), "note":note})
        #return Namespace(turn=0, bossid=int(m), note=note)
    elif re.match(r"\d+-[12345]", m):
        res.update({"turn":int(m.split("-")[0]), "bossid":int(m.split("-")[1]), "note": note})
        #return Namespace(turn=int(m.split("-")[0]), bossid=int(m.split("-")[1]), note=note)
    elif re.match(r"[a-eA-E][12345]", m):
        turn = await get_step(m[0])
        res.update({"turn":turn+1, "bossid":int(m[-1]), "note": note})
        #return Namespace(turn=turn+1, bossid=int(m[-1]), note=note)
    elif "预约表" in m:
        pass
    else:
        return None
    return Namespace(**res)
    
async def reserve(group_id: str, user_id: str, msg: Namespace):
    res = []
    if msg.cancel:
        reserved = await get_reserve(group_id=group_id, boss_id=msg.bossid)
        if reserved:
            await cancel_reserve(group_id=group_id, user_id=user_id, boss_id=msg.bossid)
            res.append({"text":"取消预约成功"})
        else:
            res.append({"text":"没有预约记录"})
    if msg.turn:
        if not msg.bossid:
            res.append({"text":"请指定预约首领编号"})
            return res
        _turn = await get_turn(group_id=group_id, boss_id=msg.bossid)
        if msg.turn == -1:
            if await get_currenthp(group_id, msg.bossid) == 0:
                res.append({"text": "当前首领不可挑战"})
            else:
                await reserve_boss(group_id=group_id, user_id=user_id, boss_id=msg.bossid, turn=-1, notes="可合刀 "+msg.note)
                res.append({"text": f"已预约合刀"})
        elif msg.turn < _turn:
            res.append({"text":"首领周目数已过号，请重新指定"})
        elif msg.turn == _turn:
            if await get_currenthp(group_id, msg.bossid) == 0:
                res.append({"text": "当前首领不可挑战"})
            else:
                await reserve_boss(group_id=group_id, user_id=user_id, boss_id=msg.bossid, turn=msg.turn, notes="可合刀 "+msg.note)
                res.append({"text":f"当前首领可以直接挑战，若想预约下一个首领，请直接使用【预约 {msg.bossid}】\n此处预约已记录，记录为【合刀请求】"})
        else:
            reserved = await get_reserve(group_id=group_id, boss_id=msg.bossid)
            if reserved:
                if reserved[0][2] == 0:
                    res.append({"text":f"您已预约过{reserved[0][3]}号首领"})
                else:
                    res.append({"text":f"您已预约过{reserved[0][2]}周目{reserved[0][3]}号首领"})
            else:
                await reserve_boss(group_id=group_id, user_id=user_id, boss_id=msg.bossid, turn=msg.turn, notes=msg.note)
                res.append({"text":f"预约{msg.turn}周目{msg.bossid}号首领成功"})
    else:
        if not msg.bossid:
            reserved = await get_reserve(group_id=group_id)
            return res
        reserved = await get_reserve(group_id=group_id, boss_id=msg.bossid)
        if reserved:
            if reserved[0][2] == 0:
                res.append({"text":f"您已预约过{reserved[0][3]}号首领"})
            else:
                res.append({"text":f"您已预约过{reserved[0][2]}周目{reserved[0][3]}号首领"})
        else:
            await reserve_boss(group_id=group_id, user_id=user_id, boss_id=msg.bossid, turn=0, notes=msg.note)
            res.append({"text":f"预约下一个{msg.bossid}号首领成功"})
    return res
    
async def reserve_report(group_id: str, boss_id: int, user_id: str = ""):
    res = []
    reserved = await get_reserve(group_id=group_id, boss_id=boss_id)
    for _group_id, user, turn, boss_id, notes in reserved:
        res.append({"at": user})
        current_turn = await get_turn(group_id=group_id, boss_id=boss_id)
        if turn == -1:
            if user_id == user:
                return []
            else:
                res.append({"text": "当前首领已击败，已自动预约下一个首领"})
            await cancel_reserve(group_id=group_id, user_id=user, boss_id=boss_id)
            await reserve_boss(group_id=group_id, user_id=user, boss_id=boss_id, turn=0, notes=notes)
        elif turn == 0 or turn == current_turn:
            res.append({"text": f"您预约的{boss_id}号首领可以挑战了"})
        elif turn != current_turn:
            if current_turn > turn:
                res.append({"text": f"您预约的{turn}周目{boss_id}号首领已过号，已自动延后预约"})
                await cancel_reserve(group_id=group_id, user_id=user, boss_id=boss_id)
                await reserve_boss(group_id=group_id, user_id=user, boss_id=boss_id, turn=0, notes=notes)
            else:
                return []
    return res 

async def reserve_list(group_id: str):
    res = []
    reserved = await get_reserve(group_id=group_id)
    if reserved:
        pass