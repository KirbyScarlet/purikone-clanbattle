## 挂树

from nonebot import on_shell_command, on_command, on_fullmatch
from nonebot.rule import ArgumentParser
from nonebot.adapters import Bot, Event, Message
from nonebot.params import ShellCommandArgs, CommandArg
from argparse import Namespace

from nonebot.adapters.satori import MessageEvent as MessageEventSatori

from .utils import check_bot, dbclient
from .status import _status

tree = on_command("挂树", rule=check_bot)
check_tree = on_command("查树", rule=check_bot)
cancel_tree = on_command("下树", aliases={"取消挂树"}, rule=check_bot)

@tree.handle()
async def _handle_tree(bot: Bot, event: Event, msg: Message = CommandArg()):
    m = msg.extract_plain_text()
    if isinstance(event, MessageEventSatori):
        group_id = event.channel.id
        user_id = event.user.id
    res = await _tree(group_id, user_id, m)
    await tree.finish(res)

@check_tree.handle()
async def _handle_check_tree(bot: Bot, event: Event, msg: Message = CommandArg()):
    m = msg.extract_plain_text()
    await check_tree.finish("#查树" + str(m))

@cancel_tree.handle()
async def _handle_cancel_tree(bot: Bot, event: Event, msg: Message = CommandArg()):
    m = msg.extract_plain_text()
    if isinstance(event, MessageEventSatori):
        group_id = event.channel.id
        user_id = event.user.id
    res = await _cancel_tree(group_id, user_id)
    await cancel_tree.finish(res)

async def get_chapter(turn: int):
    turns = await dbclient.execute_fetchall(f"SELECT chapter,turn FROM purikone_clanbattle_settings;")
    chapter = list(turns)[0][0]
    for c,t in turns:
        if turn >= int(t):
            chapter = c
    return chapter

async def get_maxhp(turn, bossid) -> int:
    c = await get_chapter(int(turn))
    return list(await dbclient.execute_fetchall(f"SELECT boss{bossid} FROM purikone_clanbattle_settings where chapter='{c}';"))[0][0]

async def get_currenthp(bossid, group_id) -> int:
    _hp = await dbclient.execute_fetchall(f"SELECT bosshp FROM purikone_clanbattle_status_{group_id} WHERE bossid={bossid} order by date desc limit 1;")
    hp = list(_hp)[0][0]
    return int(hp)

async def _tree(group_id: str, user_id: str, msg: str):
    # 检查刀手是否申请出刀
    _p = await dbclient.execute_fetchall(f"SELECT * FROM purikone_clanbattle_tree_{group_id} WHERE user='{user_id}';")
    _p = list(_p)
    if len(_p) == 0:
        return "你想挂哪颗树？请先申请出刀。"
    await dbclient.execute(f"UPDATE purikone_clanbattle_tree_{group_id} SET tree=1,info='{msg}' WHERE user='{user_id}';")
    await dbclient.commit()
    # 查当前的树
    _s = await dbclient.execute_fetchall(f"SELECT * FROM purikone_clanbattle_status_{group_id} WHERE bossid={_p[0][3]} ORDER BY date DESC LIMIT 1;")
    _s = list(_s)
    status_text = f"{_s[0][1]}-{_s[0][2]}: {await get_currenthp(_p[0][3], group_id)} / {await get_maxhp(_s[0][1], _p[0][3])}"
    return f"挂树成功\n{status_text}\n" + (await _check_tree(group_id, user_id, int(_p[0][3])))

async def _check_tree(group_id: str, user_id: str, n: int = 0):
    # 查看当前挂树情况
    if n:
        _t = await dbclient.execute_fetchall(f"SELECT * FROM purikone_clanbattle_tree_{group_id} WHERE bossid={n};")
        _t = list(_t)
        if len(_t) == 0:
            return f"当前没人挂树{n}王"
        res_text = []
        for r in _t:
            if r[2]:
                res_text.append(f"{r[1]} 已挂树 {r[-1]}")
            else:
                res_text.append(f"{r[1]} 正在挑战")
        return "\n".join(res_text)
    else:
        return await _status(group_id)

async def _cancel_tree(group_id: str, user_id: str):
    # 取消挂树
    _p = await dbclient.execute_fetchall(f"SELECT * FROM purikone_clanbattle_tree_{group_id} WHERE user='{user_id}';")
    _p = list(_p)
    if len(_p) == 0:
        return "您没有挂树，甚至没申请出刀"
    elif _p[0][2] == 0:
        return "您没有挂树"
    else:
        await dbclient.execute(f"UPDATE purikone_clanbattle_tree_{group_id} SET tree=0 WHERE user='{user_id}';")
        await dbclient.commit()
        return "取消挂树成功"
