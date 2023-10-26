# 申请出刀

from nonebot import on_shell_command, on_command, on_fullmatch
from nonebot.rule import ArgumentParser
from nonebot.adapters import Bot, Event, Message
from nonebot.params import ShellCommandArgs, CommandArg
from argparse import Namespace

from nonebot.adapters.satori import MessageEvent as MessageEventSatori

from .utils import check_bot, dbclient

apply = on_command("申请出刀", aliases={"进", "进刀"}, rule=check_bot)
cancel_apply = on_command("取消申请", aliases={"取消进"}, rule=check_bot)

async def apply_parser(msg: Message):
    m = "".join(msg.extract_plain_text().split())
    if len(m) == 1:
        if m in "12345":
            return Namespace(n=m, b=False, info="")
    elif len(m) == 2:
        if m[0] in "12345" and m[1] in "b补":
            return Namespace(n=m[0], b=True, info="")
    else:
        if m[0] in "12345" and m[1] in "b补":
            return Namespace(n=m[0], b=True, info=m[2:])
        elif m[0] in "12345":
            return Namespace(n=m[0], b=False, info=m[1:])
    return None    

@apply.handle()
async def _handle_apply(bot: Bot, event: Event, msg: Message = CommandArg()):
    args = await apply_parser(msg)
    #await apply.finish("#申请出刀\n"+str(args))
    if not args:
        await apply.finish("请检查申请参数，\n申请出刀 n [补] \n进 n [补]")
    if isinstance(event, MessageEventSatori):
        group_id = event.channel.id
        user_id = event.user.id
        user_nickname = event.member.name
    res = await _apply(group_id, user_id, user_nickname, args)
    await apply.finish(res)

@cancel_apply.handle()
async def _handle_cancel_apply(bot: Bot, event: Event, msg: Message = CommandArg()):
    if msg:
        await cancel_apply.finish()
    if isinstance(event, MessageEventSatori):
        group_id = event.channel.id
        user_id = event.user.id
    
    res = await _cancel_apply(group_id, user_id)
    await cancel_apply.finish(res)
    
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

async def _apply(group_id: str, user_id: str, user_nickname: str, args: Namespace) -> str:
    res_text = []
    # 检查有没有预约过或挂在树上
    _t = await dbclient.execute_fetchall(f"SELECT * FROM purikone_clanbattle_tree_{group_id};")
    _tree = list(_t)
    _tree_users = [x[0] for x in _tree]
    if user_id in _tree_users:
        return "你已经在出刀队列了"
    # 检查预约王当前状态
    _s = await dbclient.execute_fetchall(f"SELECT * FROM purikone_clanbattle_status_{group_id} WHERE bossid={args.n} ORDER BY date DESC limit 1;")
    _status = list(_s)
    if int(_status[0][3]) == 0:
        return "当前首领无法挑战"
    # 加入预约序列
    await dbclient.execute(f"INSERT INTO purikone_clanbattle_tree_{group_id} (user, nickname, tree, bossid, extra, info) VALUES (?,?,?,?,?,?);",(user_id, user_nickname, 0, args.n, int(bool(args.b)), ''))
    await dbclient.commit()
    res_text.append(f"{user_nickname}开始出刀\n===================")
    res_text.append(f"{_s[0][1]}-{args.n}: {await get_currenthp(args.n, group_id)} / {await get_maxhp(_s[0][1], args.n)}")
    for r in _tree:
        if int(r[3] == int(args.n)):
            if r[2]:
                res_text.append(f"{r[1]} 已挂树 {r[-1]}")
            else:
                res_text.append(f"{r[1]} 正在挑战")
    res_text.append(f"{user_nickname} 正在挑战")
    return "\n".join(res_text)

async def _cancel_apply(group_id: int, user_id: int) -> str:
    res_text = []
        # 检查有没有预约过或挂在树上
    _t = await dbclient.execute_fetchall(f"SELECT * FROM purikone_clanbattle_tree_{group_id} where user=?;", (user_id,))
    _tree = list(_t)
    _tree_users = [x[0] for x in _tree]
    if user_id in _tree_users:
        await dbclient.execute(f"DELETE FROM purikone_clanbattle_tree_{group_id} WHERE user=?;", (user_id,))
        await dbclient.commit()
        res_text.append(f"取消申请成功")
    else:
        res_text.append(f"您没有预约或挂树")
    return "\n".join(res_text)