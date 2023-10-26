### 报刀

from nonebot import on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.adapters import Bot, Event, Message
from nonebot.params import ShellCommandArgs, CommandArg
from argparse import Namespace
from nonebot.log import logger
from time import time_ns

from nonebot.adapters.satori import MessageEvent as MessageEventSatori

from .utils import check_bot, dbclient, sint
#from .utils import sint

# 有问题，暂时弃用
#report_args = ArgumentParser()
#report_args.add_argument("n", type=int, nargs="?", choices=range(1,6), help="报刀几王")
#report_args.add_argument("damage", type=str, default="0", help="伤害值")
#report_args.add_argument("extra", type=str, nargs="?", choices=("b","补"), help="是否是补偿刀")

#end_report_args = ArgumentParser()
#end_report_args.add_argument("n", type=int, nargs="?", choices=range(1,6), help="尾刀几王")
#end_report_args.add_argument("extra", type=str, nargs="?", choices=("b","补"), help="是否是补偿刀")

REPORT_HELP = """\
报刀 [几王] [伤害|尾刀] [补] [撤销]
尾刀 [几王] [补]
"""

report = on_shell_command("报刀", rule=check_bot)
end_report = on_shell_command("尾刀", rule=check_bot)

async def report_parser(msg: Message):
    m = msg.extract_plain_text().split()
    logger.info(m)
    res = {}
    if len(m) == 1:
        if m[0] == "0":
            res["n"] = "0"
            res["damage"] = None
            res["b"] = None
        else:
            res["n"] = None
            res["damage"] = m[0]
            res["b"] = None
        return Namespace(**res)
    if 2<=len(m)<=3:
        if m[0] in "12345":
            res["n"] = m[0]
            res["damage"] = m[1]
        else:
            res["n"] = None
            res["damage"] = m[0]
        if m[-1] in "b补":
            res["b"] = m[-1]
        else:
            res["b"] = None
        return Namespace(**res)
    else:
        return None
    
async def end_report_parser(msg: Message):
    m = "".join(msg.extract_plain_text().split())
    if len(m) == 1:
        if m in "12345":
            return Namespace(n=m, b=None)
        if m in "b补":
            return Namespace(n=None, b=m)
    elif len(m) == 2:
        if (m[0] in "12345") and (m[1] in "b补"):
            return Namespace(n=m[0], b=m[1])
    return None

@report.handle()
async def _handle_report(bot: Bot, event: Event, msg: Message = CommandArg()): #, args: Namespace = ShellCommandArgs()):
    args = await report_parser(msg)
    if isinstance(event, MessageEventSatori):
        user_id = event.user.id
        group_id = event.channel.id
        res = await _report(user_id, group_id, args)
    await report.finish(str(res))    

@end_report.handle()
async def _handle_end_report(bot: Bot, event: Event, msg: Message = CommandArg()):
    args = await end_report_parser(msg)
    #await end_report.finish("#尾刀\n"+str(args))
    if isinstance(event, MessageEventSatori):
        user_id = event.user.id
        group_id = event.channel.id
        res = await _end_report(user_id, group_id, args)
    await end_report.send(str(res))
    # 处理新的预约
    await end_report.finish()

async def _report(user_id: str, group_id: str, args: Namespace):
    # 检查是否申请出刀
    _a = await dbclient.execute_fetchall(f"SELECT bossid,extra FROM purikone_clanbattle_tree_{group_id} where user='{user_id}' and tree=0;")
    a = list(_a)
    if args.n is None:
        if len(a) == 0:
            return "请先申请出刀或指定王报刀"
        else:
            args.n = a[0][0]
    # 检查持否持有补偿刀
    _e = await dbclient.execute_fetchall(f"SELECT end,extra from purikone_clanbattle_history_{group_id} WHERE user='{user_id}';")
    e = list(_e)
    has_extra = bool(e) and sum([i[0] for i in e]) > sum([i[1] for i in e])
    if args.b and (not has_extra):
        return "您没有补偿刀"
    # 检查伤害数字是否合法
    try:
        damage = sint(args.damage).value
    except ValueError:
        return "伤害数值格式错误"
    # 检查当前boss是否可挑战
    _c = await dbclient.execute_fetchall(f"SELECT * from purikone_clanbattle_status_{group_id} WHERE bossid={int(args.n)} ORDER BY date DESC;")
    _, turn, bossid, bosshp, user = list(_c)[0]
    if str(bosshp) == "0":
        return "该首领无法挑战，请检查出刀记录"
    # 结算伤害
    if int(bosshp) - int(damage) <= 0:
        return "伤害超出当前首领血量，请使用 尾刀 [n]"
    current_bosshp = int(bosshp)-damage
    await dbclient.execute(f"INSERT INTO purikone_clanbattle_history_{group_id} (date, user, turn, bossid, damage, end, extra) VALUES (?,?,?,?,?,?,?);",(time_ns(), user_id, int(turn), int(bossid), int(damage), 0, int(bool(args.b))))
    await dbclient.execute(f"INSERT INTO purikone_clanbattle_status_{group_id} (date, turn, bossid, bosshp, user) VALUES (?,?,?,?,?);", (time_ns(), int(turn), int(bossid), current_bosshp, user_id))
    await dbclient.commit()

    # 取消申请
    await dbclient.execute(f"DELETE FROM purikone_clanbattle_tree_{group_id} where user='{user_id}' and bossid={args.n};")
    await dbclient.commit()
    #取消预约
    #

    return f"对{turn}-{bossid}造成了{current_bosshp}点伤害\n当前{turn}-{bossid}剩余血量{current_bosshp}"

async def get_chapter(turn: int):
    # 检查当前周目所在阶段
    turns = await dbclient.execute_fetchall(f"SELECT chapter,turn FROM purikone_clanbattle_settings;")
    chapter = list(turns)[0][0]
    for c,t in turns:
        if turn >= int(t):
            chapter = c
    return chapter

async def get_step():
    # 跨阶段前的周目
    turns = await dbclient.execute_fetchall(f"SELECT turn FROM purikone_clanbattle_settings;")
    turn = list(turns)
    turn.pop(0)
    step = [int(i[0])-1 for i in turn]
    return step

async def get_maxhp(turn, bossid) -> int:
    c = await get_chapter(int(turn))
    return list(await dbclient.execute_fetchall(f"SELECT boss{bossid} FROM purikone_clanbattle_settings where chapter='{c}';"))[0][0]

async def get_currenthp(bossid, group_id) -> int:
    _hp = await dbclient.execute_fetchall(f"SELECT bosshp FROM purikone_clanbattle_status_{group_id} WHERE bossid={bossid} order by date desc limit 1;")
    hp = list(_hp)[0][0]
    return int(hp)

async def _end_report(user_id: str, group_id: str, args: Namespace):
    """
    尾刀结算
    """
    res_text = []
    # 检查是否申请出刀
    _a = await dbclient.execute_fetchall(f"SELECT bossid,extra FROM purikone_clanbattle_tree_{group_id} where user='{user_id}' and tree=0;")
    a = list(_a)
    if args.n is None:
        if len(a) == 0:
            return "请先申请出刀或指定王报刀"
        else:
            args.n = a[0][0]
    # 检查持否持有补偿刀
    _e = await dbclient.execute_fetchall(f"SELECT end,extra from purikone_clanbattle_history_{group_id} WHERE user='{user_id}';")
    e = list(_e)
    has_extra = bool(e) and sum([i[0] for i in e]) > sum([i[1] for i in e])
    if args.b and (not has_extra):
        return "您没有补偿刀"
    # 检查当前boss是否可挑战
    _c = await dbclient.execute_fetchall(f"SELECT * from purikone_clanbattle_status_{group_id} WHERE bossid={int(args.n)} ORDER BY date DESC;")
    _, turn, bossid, bosshp, user = list(_c)[0]
    if str(bosshp) == "0":
        return "该首领无法挑战，请检查出刀记录"
    # 结算伤害
    await dbclient.execute(f"INSERT INTO purikone_clanbattle_history_{group_id} (date, user, turn, bossid, damage, end, extra) VALUES (?,?,?,?,?,?,?);",(time_ns(), user_id, int(turn), int(bossid), int(bosshp), 1, int(bool(args.b))))
    await dbclient.commit()
    res_text.append(f"对{turn}-{bossid}造成了{bosshp}点伤害")
    ## 判断该王是否进入下一周目
    _t = [list(await dbclient.execute_fetchall(f"SELECT turn FROM purikone_clanbattle_status_{group_id} WHERE bossid={i} ORDER BY date DESC;")) for i in range(1, 6)]
    _t = [int(i[0][0]) for i in _t]
    _a = [list(await dbclient.execute_fetchall(f"SELECT turn FROM purikone_clanbattle_settings;"))]
    _a = [int(i[0][0]) for i in _a]
    _step = await get_step()
    _tmax = max(_t)
    _tmin = min(_t)
    _tavg = sum(_t)/5
    date = time_ns()
    if _tmax in _step:   # 检查当前是否有王在跨阶段周目
        if turn == _tmax:  # 当前王也在准备跨阶段，则直接扣除血量不跨阶段
            await dbclient.execute(f"INSERT INTO purikone_clanbattle_status_{group_id} (date, turn, bossid, bosshp, user) VALUES (?,?,?,?,?);", (date, int(turn), int(bossid), 0, user_id))
            await dbclient.commit()
            _status = [await get_currenthp(i, group_id) for i in range(1,6)]
            if sum(_status) == 0: # 跨阶段周目全部出完
                for i in range(1, 6): #全部进入下周目
                    await dbclient.execute(f"INSERT INTO purikone_clanbattle_status_{group_id} (date, turn, bossid, bosshp, user) VALUES (?,?,?,?,?);", (date+1, int(turn)+1, i, await get_maxhp(turn+1, i), user_id))
                    await dbclient.commit()
                res_text.append(f"当前{int(turn)+1}-{bossid}剩余血量{await get_maxhp(int(turn)+1, bossid)}")
            else:
                res_text.append(f"{turn}-{bossid}无法继续挑战")
        else: # 当前王不跨阶段，则该王进下一周目
            await dbclient.execute(f"INSERT INTO purikone_clanbattle_status_{group_id} (date, turn, bossid, bosshp, user) VALUES (?,?,?,?,?);", (date, int(turn)+1, int(bossid), await get_maxhp(turn, bossid), user_id))
            await dbclient.commit()
            res_text.append(f"当前{int(turn)+1}-{bossid}剩余血量{await get_maxhp(turn, bossid)}")
    else:  #当前不跨阶段
        if _tmin == _tmax: # 当前所有王在相同阶段
            await dbclient.execute(f"INSERT INTO purikone_clanbattle_status_{group_id} (date, turn, bossid, bosshp, user) VALUES (?,?,?,?,?);", (date, int(turn)+1, int(bossid), await get_maxhp(turn, bossid), user_id))
            await dbclient.commit()
            res_text.append(f"当前{int(turn)+1}-{bossid}剩余血量{await get_maxhp(turn, bossid)}")
        elif turn == _tmax: # 当前王出完后不可再挑战 
            await dbclient.execute(f"INSERT INTO purikone_clanbattle_status_{group_id} (date, turn, bossid, bosshp, user) VALUES (?,?,?,?,?);", (date, int(turn), int(bossid), 0, user_id))
            await dbclient.commit()
            res_text.append(f"{turn}-{bossid}无法继续挑战")
        else: #该王进入下一阶段，并判断当前是否存在不可挑战的王并进入下已周目
            await dbclient.execute(f"INSERT INTO purikone_clanbattle_status_{group_id} (date, turn, bossid, bosshp, user) VALUES (?,?,?,?,?);", (date, int(turn)+1, int(bossid), await get_maxhp(turn, bossid), user_id))
            await dbclient.commit()
            res_text.append(f"当前{int(turn)+1}-{bossid}剩余血量{await get_maxhp(turn, bossid)}")
            _status = [await get_currenthp(i, group_id) for i in range(1,6)]
            if _tavg > _tmax-0.3: 
                for i in range(1,6):
                    if _status[i-1] == 0:
                        await dbclient.execute(f"INSERT INTO purikone_clanbattle_status_{group_id} (date, turn, bossid, bosshp, user) VALUES (?,?,?,?,?);", (date, int(turn)+2, i, await get_maxhp(turn+1, i), user_id))
                        await dbclient.commit()
    # 取消申请
    await dbclient.execute(f"DELETE FROM purikone_clanbattle_tree_{group_id} where bossid={args.n};")
    await dbclient.commit()
    #取消预约
    #

    return "\n".join(res_text)
