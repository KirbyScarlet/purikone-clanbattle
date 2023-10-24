# 查看当前状态

from nonebot import on_shell_command, on_command
from nonebot.rule import ArgumentParser

from nonebot.adapters import Bot, Event, Message
from nonebot.params import ShellCommandArgs, CommandArg
from nonebot.log import logger

from argparse import Namespace
from time import time_ns

from nonebot.adapters.satori import MessageEvent as MessageEventSatori

from .utils import check_bot, dbclient, sint

status = on_command("状态", aliases={"进度"}, rule=check_bot)

@status.handle()
async def _handle_status(bot: Bot, event: Event, msg: Message = CommandArg()):
    if isinstance(event, MessageEventSatori):
        group_id = event.channel.id
    res = await _status(group_id)
    await status.finish(res)

async def get_chapter(turn: int):
    turns = await dbclient.execute_fetchall(f"SELECT chapter,turn FROM purikone_clanbattle_settings;")
    chapter = list(turns)[0][0]
    for c,t in turns:
        if turn >= int(t):
            chapter = c
    return chapter

async def _status(group_id: str):
    st = []
    for i in range(1,6):
        b = await dbclient.execute_fetchall(f"SELECT * FROM purikone_clanbattle_status_{group_id} where bossid={i} order by date desc limit 1;")
        logger.info(str(b))
        if len(b) == 0:
            maxhp = list(await dbclient.execute_fetchall(f"SELECT boss{i} FROM purikone_clanbattle_settings where chapter='a';"))[0][0]
            st.append(f"==========\n1-{i}: {maxhp} / {maxhp}")
            await dbclient.execute(f"INSERT INTO purikone_clanbattle_status_{group_id} VALUES (?,?,?,?,?)",(time_ns(), 1, i, maxhp, 0))
            await dbclient.commit()
        else:
            maxhp = list(await dbclient.execute_fetchall(f"SELECT boss{i} FROM purikone_clanbattle_settings where chapter='{await get_chapter(b[0][1])}';"))[0][0]
            st.append(f"==========\n{b[0][1]}-{b[0][2]}: {b[0][3]} / {maxhp}")
    
    title = "今日已出{count}刀\n"

    return title + "\n".join(st)

    