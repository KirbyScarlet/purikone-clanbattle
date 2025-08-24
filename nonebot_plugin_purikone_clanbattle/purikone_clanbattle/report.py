### 报刀

from argparse import Namespace
from nonebot.adapters import Message
from nonebot.log import logger

from .utils.sqliteapi import (
    on_tree,
    get_status,
    boss_status,
    get_chapter,
    get_turn,
    get_step,
    get_maxhp,
    get_currenthp,
    update_bosshp,
    compensiated,
    update_history,
    cancel_challenge,
    cancel_reserve,
    get_reserve,
)
from .reserve import reserve_report
from .utils import sint

# 有问题，暂时弃用
#report_args = ArgumentParser()
#report_args.add_argument("n", type=int, nargs="?", choices=range(1,6), help="报刀几王")
#report_args.add_argument("damage", type=str, default="0", help="伤害值")
#report_args.add_argument("extra", type=str, nargs="?", choices=("b","补"), help="是否是补偿刀")

#end_report_args = ArgumentParser()
#end_report_args.add_argument("n", type=int, nargs="?", choices=range(1,6), help="尾刀几王")
#end_report_args.add_argument("extra", type=str, nargs="?", choices=("b","补"), help="是否是补偿刀")

REPORT_HELP = """\
命令格式：
  报刀 [首领编号] 伤害值 [补(b)]
  尾刀 [首领编号] [补(b)]
  报刀 撤销
例：
  报刀 5 3000w
  报刀 2 200w b
  报刀 2200w （已申请出刀）
  报刀 300w b （已申请出刀）
"""

async def report_parser(msg: Message):
    m = msg.extract_plain_text().split()
    res = {
        "n": 0,
        "damage": None,
        "b": None,
        "revoke": None,
    }
    if len(m) == 1:
        if m[0] == "0":
            res["n"] = -1
        else:
            res["damage"] = m[0]
        return Namespace(**res)
    elif 2<=len(m)<=3:
        if m[0] in "12345":
            res["n"] = int(m[0])
            res["damage"] = m[1]
        else:
            res["damage"] = m[0]
        if m[-1] in "b补":
            res["b"] = m[-1]
        else:
            res["b"] = None
        return Namespace(**res)
    elif "撤销" in m:
        res["revoke"] = True
        return Namespace(**res)
    else:
        return None
    
async def end_report_parser(msg: Message):
    m = "".join(msg.extract_plain_text().split())
    res = {
        "n": 0,
        "b": None,
        "revoke": None,
    }
    if len(m) == 0:
        return Namespace(**res)
    if len(m) == 1:
        if m in "12345":
            res["n"] = int(m)
        if m in "b补":
            res["b"] = True
        return Namespace(**res)
    elif len(m) == 2:
        if (m[0] in "12345") and (m[1] in "b补"):
            res["n"] = int(m[0])
            res["b"] = True
            return Namespace(**res)
    if "撤销" in m:
        res["revoke"] = True
        return Namespace(**res)

async def report(group_id: str, user_id: str, args: Namespace):
    # 检查是否申请出刀
    res = []
    if args.n == -1:
        return [{"text": "已记录"}]
    _t, _b, _c, _n = await on_tree(group_id, user_id)
    if not (_b or args.n):
        return [{"text":"\n请先 申请出刀 或 指定首领编号报刀\n"+REPORT_HELP}]
    logger.info(f"{_b}")
    if _b and args.n and int(args.n) != int(_b):
        res.append({"text": "您报刀首领与申请首领不一致，以当前命令获取的首领编号执行后续操作\n"})
    boss_id = (args.n or _b)
    # 检查持否持有补偿刀
    _c = await compensiated(group_id, user_id)
    if (args.b and not _c):
        return [{"text": "您没有补偿刀"}]
    # 检查伤害数字是否合法
    try:
        damage = sint(args.damage).value
    except ValueError:
        return [{"text": "伤害数值格式错误\n数值格式：\n  数字，数字k，数字w，数字e\n  20000000，2000w，2kw，0.2e"}]
    # 检查当前boss是否可挑战
    bosshp = await get_currenthp(group_id, (args.n or _b))
    if bosshp == 0:
        return [{"text": "该首领无法挑战，请检查出刀记录"}]
    # 结算伤害
    if bosshp - damage <= 0:
        return [{"text": "伤害超出当前首领血量，请重新报刀，并使用命令 尾刀 [首领编号] [补(b)]"}]
    current_bosshp = bosshp-damage
    turn = await get_turn(group_id, boss_id)
    await update_bosshp(group_id, boss_id, user_id, turn, current_bosshp)
    await update_history(group_id, boss_id, user_id, turn, damage, 0, int(bool(args.b)))

    # 取消当前报刀人的出刀申请
    await cancel_challenge(group_id, user_id=user_id)
    #取消预约
    await cancel_reserve(group_id, user_id, boss_id)

    res.append({"text": f"对{turn}周目{boss_id}号首领造成了{damage}点伤害\n当前【{turn}-{boss_id}】剩余血量{current_bosshp}"})

    return res

async def end_report(group_id: str, user_id: str, args: Namespace):
    """
    尾刀结算
    """
    # 检查是否申请出刀
    res = []
    _t, _b, _c, _n = await on_tree(group_id, user_id)
    if not (_b or args.n):
        return [{"text":"\n请先 申请出刀 或 指定首领编号报刀\n"+REPORT_HELP}]
    if _b and args.n and int(args.n) != int(_b):
        res.append({"text": "您报刀首领与预约首领不一致，以当前命令获取的首领编号执行后续操作"})
    boss_id = (args.n or _b)
    # 检查持否持有补偿刀
    _c = await compensiated(group_id, user_id)
    if args.b and not _c:
        return [{"text": "您没有补偿刀"}]
    # 检查当前boss是否可挑战
    bosshp = await get_currenthp(group_id, boss_id)
    if bosshp == 0:
        return [{"text": "该首领无法挑战，请检查出刀记录"}]
    # 结算伤害
    turn = await get_turn(group_id, boss_id)
    #await update_bosshp(group_id, boss_id, user_id, turn, bosshp)
    await update_history(group_id, boss_id, user_id, turn, bosshp, 1, int(bool(args.b)))
    res.append({"text": f"对{turn}周目{boss_id}号首领造成了{bosshp}点伤害\n"})
    ## 判断该王是否进入下一周目
    _t = [await get_turn(group_id, i) for i in range(1, 6)]
    _step = await get_step()
    _tmax = max(_t)
    _tmin = min(_t)
    _tavg = sum(_t)/5
    if _tmax in _step:   # 检查当前是否有王在跨阶段周目
        if turn == _tmax:  # 当前王也在准备跨阶段，则直接扣除血量不跨阶段，上方已结算
            await update_bosshp(group_id, boss_id, user_id, turn, 0)
            _status = [await get_currenthp(group_id, i) for i in range(1,6)]
            if sum(_status) == 0: # 跨阶段周目全部出完
                for i in range(1, 6): #全部进入下周目
                    await update_bosshp(group_id, i, user_id, int(turn)+1, await get_maxhp(turn+1, i))
                res.append({"text": f"当前【{int(turn)+1}-{boss_id}】剩余血量{await get_maxhp(int(turn)+1, boss_id)}"})
                res.extend(await reserve_report(group_id, i))
            else:
                res.append({"text": f"【{turn}-{boss_id}】无法继续挑战"})
        else: # 当前王不跨阶段，则该王进下一周目
            await update_bosshp(group_id, boss_id, user_id, turn+1, await get_maxhp(turn+1, boss_id))
            res.append({"text": f"当前【{int(turn)+1}-{boss_id}】剩余血量{await get_maxhp(turn, boss_id)}\n"})
            res.extend(await reserve_report(group_id, boss_id))
    else:  #当前不跨阶段
        if _tmin == _tmax: # 当前所有王在相同阶段
            await update_bosshp(group_id, boss_id, user_id, turn+1, await get_maxhp(turn, boss_id))
            res.append({"text": f"当前【{int(turn)+1}-{boss_id}】剩余血量{await get_maxhp(turn, boss_id)}"})
            res.extend(await reserve_report(group_id, boss_id))
        elif turn == _tmax: # 当前王出完后不可再挑战 
            await update_bosshp(group_id, boss_id, user_id, turn, 0)
            res.append({"text": f"【{turn}-{boss_id}】无法继续挑战"})
        else: #该王进入下一阶段，并判断当前是否存在不可挑战的王并进入下已周目
            await update_bosshp(group_id, boss_id, user_id, turn+1, await get_maxhp(turn+1, boss_id))
            res.append({"text": f"当前【{int(turn)+1}-{boss_id}】剩余血量{await get_maxhp(turn, boss_id)}"})
            res.extend(await reserve_report(group_id, boss_id))
            _status = [await get_currenthp(group_id, i) for i in range(1,6)]
            if _tavg > _tmax-0.3: # 只剩自己在较低阶段，剩下4个的平均数为.8。到底是寄巧，还是大雷，我不知道
                for i in range(1,6):
                    if _status[i-1] == 0:
                        await update_bosshp(group_id, i, user_id, turn+2, await get_maxhp(turn, i))
                        res.extend(await reserve_report(group_id, i))
    # 取消申请
    await cancel_challenge(group_id, boss_id=boss_id)
    # 取消预约
    await cancel_reserve(group_id, user_id, boss_id)

    return res
