#

__all__ = []

from argparse import Namespace
from nonebot.adapters import Message

from .utils.sqliteapi import (
    get_chapter,
    boss_status,
    get_maxhp,
    get_turn,
    get_status,
    get_currenthp,
    update_bosshp,
    get_step
)

from .utils import sint

import re

MODIFY_HELP = """\
命令格式：
  修改 首领编号:首领血量[或百分比]
  修改 周目-编号:[首领血量[或百分比]]
  修改 撤销
例：
  修改 3:4kw  
  【修改当前周目3号首领生命值为4kw】
  修改 42-3
  【修改当前3号首领的周目数为42】
  修改 42-3:100%  
  【修改3王周目数为42，生命值修改为满血】
  修改 2:100% 43-3:0 4:1e
  【同时修改多个首领的状态】"""

parser = re.compile(r"((?P<turn>[1-9]\d?)-)?(?P<bossid>[1-5])[:：]?((?P<maxhp>(100%)$)|(?P<hp>(\d+)?(\.\d+)?k?w?e?)$)?")

async def modify_parser(msg: Message) -> Namespace:
    res = {
        "modify": [],  # list[dict]
        "error": []   # list[str]
    }
    for m in msg.extract_plain_text().split():
        p = parser.match(m).groupdict()
        if not p["bossid"] or not (p["turn"] or p["hp"] or p["maxhp"]):
            res["error"].append({"text": f"{m} 命令格式错误\n+{MODIFY_HELP}"})
        else: 
            res["modify"].append(p)
    for i in range(len(res["modify"])):
        res["modify"][i]["bossid"] = int(res["modify"][i]["bossid"])
        res["modify"][i]["turn"] = int(res["modify"][i]["turn"])
        res["modify"][i]["maxhp"] = bool(res["modify"][i]["maxhp"])
        if res["modify"][i]["maxhp"]:
            res["modify"][i]["hp"] = 0
        if res["modify"][i]["hp"] is not None:
            try:
                res["modify"][i]["hp"] = sint(res["modify"][i]["hp"])
            except ValueError:
                res["error"].append({"text": f"{m} 血量格式错误\n{sint.__doc__}"})
        else:
            res["modify"][i]["hp"] = 0
    if not res["modify"] and not res["error"]:
        res["error"].append({"text": MODIFY_HELP})
    return Namespace(**res)

async def modify(group_id: str, args: Namespace):
    res = []
    _modify = True
    _t = [await get_turn(group_id, i) for i in range(1, 6)]
    _hp = [await get_currenthp(group_id, i) for i in range(1, 6)]
    for m in args.modify:
        if m["turn"]:
            _t[m["bossid"]-1] = m["turn"]
        if m["maxhp"]:
            _hp[m["bossid"]-1] = await get_maxhp(m["turn"], m["bossid"])
        elif m["hp"]:
            _hp[m["bossid"]-1] = m["hp"].value
    _step = await get_step()
    _max = max(_t)
    _min = min(_t)
    if _max-_min > 1:
        return [{"text": f"修改后的周目数错误\n{' '.join([f'{i}-{j}' for i,j in zip(_t, range(1,6))])}"}]
    if _min in _step and _max not in _step:
        return [{"text": f"{_min}周目和{_max}为跨阶段周目，请检查游戏内周目数"}]
    for i in range(5):
        if _t[i] == _min and _hp[i] == 0:
            return [{"text": f"{m['turn']}-{m['bossid']} 修改该boss血量为0时将进行跨周目结算，请检查指定的周目数或血量是否正确。"}]
    for m in args.modify:
        await update_bosshp(group_id, m["bossid"], "0", _t[m["bossid"]-1], _hp[m["bossid"]-1])
        res.append({"text": f"【{m['turn']}-{m['bossid']}】修改为 {_hp[m['bossid']-1]}/{await get_maxhp(_t[m['bossid']-1], m['bossid'])}\n"})
    return res
