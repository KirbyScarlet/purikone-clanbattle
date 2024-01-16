# 申请出刀

from argparse import Namespace
from nonebot.adapters import Message
from .utils.sqliteapi import (
    on_tree, 
    get_maxhp, 
    get_currenthp,
    start_challenge,
    get_turn,
    get_status,
    cancel_challenge
)

APPLY_HELP = """\
命令格式：
  申请出刀 首领编号 [是否补偿]
例：
  申请出刀 2
  申请出刀 3 b"""

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

async def apply(group_id: str, user_id: str, args: Namespace) -> list[dict]:
    res_text = []
    # 检查有没有预约过或挂在树上
    _t, _b, _c, n = await on_tree(group_id, user_id)
    if _t:
        return [{"text": "你已经在出刀队列了"}]
    # 检查预约王当前状态
    hp = await get_currenthp(group_id, args.n)
    if hp == 0:
        return [{"text": "当前首领无法挑战"}]
    # 加入预约序列
    await start_challenge(group_id, user_id, args.n, args.b, args.info)
    res_text.append({"text": "开始出刀\n===================\n"})
    turn = await get_turn(group_id, args.n)
    res_text.append({"text":f"{turn}-{args.n}: {hp} / {await get_maxhp(turn, args.n)}\n"})
    for r in await get_status(group_id, args.n):
        if r[1]:
            res_text.append({"at":f"{r[0]}"})
            res_text.append({"text": f"已挂树 {r[-1]}\n"})
        else:
            res_text.append({"at":f"{r[0]}"})
            res_text.append({"text": f"正在挑战 {r[-1]}\n"})
    return res_text

async def cancel_apply(group_id: int, user_id: int) -> str:
    res_text = []
        # 检查有没有预约过或挂在树上
    _t = on_tree(group_id, user_id)
    if _t:
        await cancel_challenge(group_id, user_id)
        res_text.append({"text": f"取消申请成功"})
    else:
        res_text.append({"text": f"你还没有预约过呢"})
    return res_text
