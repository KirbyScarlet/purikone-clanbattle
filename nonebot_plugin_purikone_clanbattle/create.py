# 创建公会会战

from nonebot import on_command
from nonebot.rule import ArgumentParser
from nonebot.adapters import Bot, Event, Message
from nonebot.params import ShellCommandArgs, CommandArg
from argparse import Namespace

from nonebot.adapters.satori import MessageEvent as MessageEventSatori

from .utils import dbclient, check_bot

create = on_command("创建会战", aliases={"会战开始", "工会战开始"}, rule=check_bot)

@create.handle()
async def _create(bot: Bot, event: Event, msg: Message = CommandArg()):
    if isinstance(event, MessageEventSatori):
        group_id = event.channel.id
    try:
        await _create_db(group_id)
    except Exception as e:
        await create.finish("数据库连接错误\n"+ str(e))
    await create.finish(f"本群会战已开启 {group_id}")


# 急着先上线在自己群用，注入问题到时候再改
async def _create_db(group_id):
    groupid = str(group_id)
    # 基础设置表 阶段开始的周目，boss血量[1-5]
    await dbclient.execute(f"""\
CREATE TABLE purikone_clanbattle_settings(
    chapter TEXT,
    turn INTEGER,
    boss1 TEXT,
    boss2 TEXT,
    boss3 TEXT,
    boss4 TEXT,
    boss5 TEXT
);
""")
    # 申请出刀表 用户id 周目 几王 是否是补偿 额外文字信息
    await dbclient.execute(f"""\
CREATE TABLE purikone_clanbattle_apply_{groupid}(
    user TEXT,
    turn TEXT,
    boss INTEGER,
    extra INTEGER,
    info TEXT
);""")
    # 挂树表 用户id 几王 刀型是否补偿刀 额外文字信息
    await dbclient.execute(f"""\
CREATE TABLE purikone_clanbattle_tree_{groupid}(
    user TEXT,
    bossid INTEGER,
    extra INTEGER,
    info TEXT
);""")
    # 当前血量记录表 当前周目数 几王 当前王血量 最近一个对此boss造成伤害的出刀人
    await dbclient.execute(f"""\
CREATE TABLE purikone_clanbattle_status_{groupid}(
    date INTEGER,
    turn INTEGER,
    bossid INTEGER,
    bosshp INTEGER,
    user TEXT
);""")
    # 刀手出刀记录表 日期 刀手 周目 几王 伤害 是否尾刀
    await dbclient.execute(f"""\
CREATE TABLE purikone_clanbattle_history_{groupid}(
    date INTEGER,
    user TEXT,
    turn INTEGER,
    bossid INTEGER,
    damage INTEGER,
    extra, INTEGER
);""")
    # 预约表 刀手 周目 几王 额外文字信息
    await dbclient.execute(f"""\
CREATE TABLE purikone_clanbattle_reserve_{groupid}(
    user TEXT,
    turn INTEGER,
    bossid INTEGER,
    info TEXT
);""")
    await dbclient.commit()
