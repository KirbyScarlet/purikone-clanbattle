import asyncio
import datetime
import aiosqlite
import time
import pathlib
from nonebot import get_driver
from .config import purikone_config

if not pathlib.Path("data/purikone").exists():
    pathlib.Path("data/purikone").mkdir(parents=True, exist_ok=True)

DB_PATH = pathlib.Path("data/purikone/purikone_clanbattle.db")

dbclient = asyncio.run(aiosqlite.connect(DB_PATH).__aenter__())

@get_driver().on_startup
async def _():
    try:
        await dbclient.execute("select * from purikone_clanbattle_group")
    except:
        await init_db()
    print(purikone_config.purikone_clanbattle_settings)
    for server in purikone_config.purikone_clanbattle_settings:
        r = await dbclient.execute_fetchall("select * from purikone_clanbattle_settings WHERE server=?", (server,))
        if not r:
            for items in purikone_config.purikone_clanbattle_settings[server]:
                await dbclient.execute("INSERT INTO purikone_clanbattle_settings VALUES(?,?,?,?,?,?,?,?)", (server, *items))
            await dbclient.commit()

@get_driver().on_shutdown
async def _():
    await dbclient.close()

async def init_db():
    """
    初始化
    """
    # 记录群组是否开启会战
    await dbclient.execute(f"""\
CREATE TABLE purikone_clanbattle_group(
    groupid TEXT,
    server TEXT,
    date INTEGER
);""")
    # 设置，阶段首领信息
    await dbclient.execute(f"""\
CREATE TABLE purikone_clanbattle_settings(
    server TEXT,
    chapter TEXT,
    turn INTEGER,
    boss1 TEXT,
    boss2 TEXT,
    boss3 TEXT,
    boss4 TEXT,
    boss5 TEXT
);
""")
    # （官方bot）因为官方bot无法获取用户信息，需要用户自行上传昵称
    await dbclient.execute(f"""
CREATE TABLE purikone_clanbattle_user(
    groupid TEXT,
    user TEXT,
    nickname TEXT
);""")
    # 挂树表 用户id 几王 刀型是否补偿刀 额外文字信息
    await dbclient.execute(f"""\
CREATE TABLE purikone_clanbattle_tree(
    groupid TEXT,
    user TEXT,
    tree INTEGER,
    bossid INTEGER,
    compensiate INTEGER,
    notes TEXT
);""")
    # 当前血量记录表 当前周目数 几王 当前王血量 最近一个对此boss造成伤害的出刀人
    await dbclient.execute(f"""\
CREATE TABLE purikone_clanbattle_status(
    groupid TEXT,
    date INTEGER,
    turn INTEGER,
    bossid INTEGER,
    bosshp INTEGER,
    user TEXT
);""")
    # 刀手出刀记录表 日期 刀手 周目 几王 伤害 是否收尾刀 是否是尾刀造成的伤害
    await dbclient.execute(f"""\
CREATE TABLE purikone_clanbattle_history(
    groupid TEXT,
    date INTEGER,
    user TEXT,
    turn INTEGER,
    bossid INTEGER,
    damage INTEGER,
    end INTEGER,
    compensiate, INTEGER
);""")
    # 预约表 刀手 周目 几王 额外文字信息
    await dbclient.execute(f"""\
CREATE TABLE purikone_clanbattle_reserve(
    groupid TEXT,
    user TEXT,
    turn INTEGER,
    bossid INTEGER,
    notes TEXT
);""")
    await dbclient.commit()

async def group_check(group_id: str) -> tuple[str, str]:
    """
    检查当前群是否开启会战
    return 服务器地区，开始会战时间
    """
    _t = await dbclient.execute_fetchall("SELECT server,date from purikone_clanbattle_group WHERE groupid=?", (group_id,))
    _t = list(_t)
    if _t:
        return _t[0][0], _t[0][1]
    else:
        return None, None
    
async def group_set(group_id: str, server: str):
    """
    开启会战
    """
    #_d = dbclient.execute_fetchall("SELECT date FROM purikone_clanbattle_group WHERE server=? and groupid='0';", (server,))
    #_d = list(_d)
    #date = int(datetime.datetime.fromisoformat(_d[0][0]).timestamp())*10**9
    date = time.time_ns()
    await dbclient.execute("INSERT INTO purikone_clanbattle_group VALUES (?,?,?)", (group_id, server, date))
    await dbclient.commit()
    # 初始化首领生命值
    for i in range(1,6):
        _maxhp = await get_maxhp(1, i)
        await dbclient.execute("INSERT INTO purikone_clanbattle_status VALUES (?,?,?,?,?,?)",(group_id, date, 1, i, _maxhp, "0"))
        await dbclient.commit()
    return

async def group_server(group_id: str):
    """
    获取当前群的服务器
    """
    _t = await dbclient.execute_fetchall("SELECT server from purikone_clanbattle_group WHERE groupid=?", (group_id,))
    _t = list(_t)
    if _t:
        return _t[0][0]
    else:
        return None

async def group_reset(group_id: str):
    """
    重置会战
    """
    await dbclient.execute("DELETE FROM purikone_clanbattle_status WHERE groupid=?", (group_id,))
    await dbclient.commit()
    date = time.time_ns()
    for i in range(1,6):
        _maxhp = await get_maxhp(1, i)
        await dbclient.execute("INSERT INTO purikone_clanbattle_status VALUES (?,?,?,?,?,?)",(group_id, date, 1, i, _maxhp, "0"))
        await dbclient.commit()
    return

async def add_group(group_id: str, user_id: str, nickname: str):
    """
    加入会战，仅作记录
    """
    # 检查是否已加入
    _d = await dbclient.execute_fetchall(
        "SELECT * FROM purikone_clanbattle_user WHERE groupid = ? AND user = ?", (group_id, user_id))
    _d = list(_d)
    if _d:
        await dbclient.execute("UPDATE purikone_clanbattle_user SET nickname = ? WHERE groupid = ? AND user = ?", (nickname, group_id, user_id))
        await dbclient.commit()
        return True   # 更新成功
    else:
        await dbclient.execute("INSERT INTO purikone_clanbattle_user VALUES (?,?,?)", (group_id, user_id, nickname))
        await dbclient.commit()
        return False   # 新增成功

async def exit_group(group_id: str, user_id: str):
    """
    删除加入会战的记录
    """
    await dbclient.execute("DELETE FROM purikone_clanbattle_user WHERE groupid = ? AND user = ?", (group_id, user_id))
    await dbclient.commit()
    return

async def get_group_members(*, group_id: str = None, user_id: str = None):
    """
    获取会战成员
    """
    if user_id:
        _d = await dbclient.execute_fetchall("SELECT nickname from purikone_clanbattle_user WHERE user=?", (user_id,))
        _d = list(_d)
        if _d:
            return _d[0][0]
        else:
            return None
    if group_id:
        _d = await dbclient.execute_fetchall(
        "SELECT * FROM purikone_clanbattle_user WHERE groupid = ?", (group_id,))
        return list(_d)

async def on_tree(group_id: str, user_id: str) -> list[bool, int, bool, str]:
    """
    检查刀手是否在树上
    返回值：
    [是否在树上，首领编号，该刀是否是补偿刀，文字信息]
    """
    _t = await dbclient.execute_fetchall(
        "SELECT tree,bossid,compensiate,notes FROM purikone_clanbattle_tree WHERE groupid = ? AND user = ?",
        (group_id, user_id)
    )
    _t = list(_t)
    if bool(len(_t)):
        return _t[0]
    else:
        return [False, 0, False, ""]

async def climb_tree(group_id: str, user_id: str, notes: str = ""):
    """
    挂树
    """
    await dbclient.execute("UPDATE purikone_clanbattle_tree SET tree=1,notes=? WHERE groupid=? AND user=?", (notes, group_id, user_id))
    await dbclient.commit()
    return

async def fell_tree(group_id: str, user_id: str):
    """
    下树
    """
    await dbclient.execute("UPDATE purikone_clanbattle_tree SET tree=0 WHERE groupid=? AND user=?", (group_id, user_id))
    await dbclient.commit()
    return

async def get_status(group_id: str, boss_id: int = 0):
    """
    查树上多少人
    """
    if boss_id:
        _t = await dbclient.execute_fetchall("SELECT user,tree,notes FROM purikone_clanbattle_tree WHERE groupid=? AND bossid=?", (group_id, boss_id))
    else:
        _t = await dbclient.execute_fetchall("SELECT user,tree,notes FROM purikone_clanbattle_tree WHERE groupid=?", (group_id,))
    return list(_t)

async def start_challenge(
        group_id: str, 
        user_id: str, 
        boss_id: int,
        compensiate: bool = False,
        notes: str = ""):
    """
    开始挑战首领
    """
    _t = await dbclient.execute("INSERT INTO purikone_clanbattle_tree (groupid, user, tree, bossid, compensiate, notes) VALUES (?, ?, ?, ?, ?, ?)", (group_id, user_id, 0, boss_id, int(compensiate), notes))
    await dbclient.commit()
    return

async def cancel_challenge(
        group_id: str,
        user_id: str = None,
        boss_id: int|str = None):
    """
    取消挑战
    """
    if user_id and boss_id:
        await dbclient.execute("DELETE FROM purikone_clanbattle_tree WHERE groupid=? AND user=? AND bossid=?", (group_id, user_id, boss_id))
        await dbclient.commit()
    elif user_id:
        await dbclient.execute("DELETE FROM purikone_clanbattle_tree WHERE groupid=? AND user=?", (group_id, user_id))
        await dbclient.commit()
    elif boss_id:
        await dbclient.execute("DELETE FROM purikone_clanbattle_tree WHERE groupid=? AND bossid=?", (group_id, boss_id))
        await dbclient.commit()
    return

async def boss_status(group_id: str, boss_id: int):
    """
    检查当前首领是否可挑战
    """
    _t = await dbclient.execute_fetchall(
        "SELECT bosshp FROM purikone_clanbattle_status WHERE groupid = ? AND bossid = ? ORDER BY date DESC limit 1",
        (group_id, boss_id)
    )
    _t = list(_t)
    return bool(_t[0][0])

async def compensiated(
        group_id: str,
        user_id: str):
    """
    检查当前刀手是否持有补偿刀
    """
    _t = await dbclient.execute_fetchall("SELECT end, compensiate FROM purikone_clanbattle_history WHERE groupid=? AND user=?", (group_id, user_id))
    _t = list(_t)
    if _t:
        _end = [1 for i in _t if i[1]]
        _comp = [1 for i in _t if i[0]==1 and i[1]!=1]
        return _comp > _end
    else:
        return False

async def get_chapter(turn: int):
    """
    获取当前周目阶段
    """
    _t = await dbclient.execute_fetchall("SELECT chapter,turn FROM purikone_clanbattle_settings;")
    _t = list(_t)
    chapter = list(_t)[0][0]
    for c,t in _t:
        if turn >= int(t):
            chapter = c
    return chapter

async def get_turn(
        group_id: str,
        boss_id: int
):
    _t = await dbclient.execute_fetchall(f"SELECT turn FROM purikone_clanbattle_status WHERE groupid=? AND bossid=? ORDER BY date DESC limit 1;", (group_id, boss_id))
    if not _t:
        await update_bosshp(group_id, boss_id, "0", 1, await get_maxhp(1, boss_id))
        _t = [[await get_maxhp(1, boss_id)]]
    return int(list(_t)[0][0])

async def get_step(chapter: str = ""):
    """
    跨阶段前的周目
    """
    turns = await dbclient.execute_fetchall(f"SELECT turn FROM purikone_clanbattle_settings;")
    turn = list(turns)
    turn.pop(0)
    step = [int(i[0])-1 for i in turn]
    return step

async def get_maxhp(turn: int, bossid: int) -> int:
    """
    获取阶段首领最大血量
    """
    c = await get_chapter(int(turn))
    _t = await dbclient.execute_fetchall(f"SELECT boss{bossid} FROM purikone_clanbattle_settings where chapter=?", (c,))
    return list(_t)[0][0]

async def get_currenthp(group_id: str, boss_id: int) -> int:
    """
    首领当前生命值
    """
    _hp = await dbclient.execute_fetchall(f"SELECT bosshp FROM purikone_clanbattle_status WHERE groupid=? AND bossid=? ORDER BY date DESC LIMIT 1;", (group_id, boss_id))
    hp = list(_hp)[0][0]
    return int(hp)

async def update_bosshp(
        group_id: str, 
        boss_id: int, 
        user_id: str,
        turn: int,
        hp: int):
    """
    结算伤害
    """
    date = time.time_ns()
    await dbclient.execute(f"INSERT INTO purikone_clanbattle_status (groupid, date, turn, bossid, bosshp, user) VALUES (?,?,?,?,?,?);", (group_id, date, turn, boss_id, hp, user_id))
    await dbclient.commit()
    return

async def update_history(
        group_id: str,
        boss_id: int,
        user_id: str,
        turn: int,
        damage: int,
        end: int,
        compensiate: int
):
    date = time.time_ns()
    await dbclient.execute(f"INSERT INTO purikone_clanbattle_history (groupid, date, user, turn, bossid, damage, end, compensiate) VALUES (?,?,?,?,?,?,?,?);",(group_id, date, user_id, turn, boss_id, damage, end, compensiate))
    await dbclient.commit()

def get_today_start_time(server="B"):
    """
    获取结算周期的纳秒时间戳
    """
    offset = {
        "B": 3, # 国服结算时间为5:00 utc+8，国际标准时间为昨天晚上21点
        "J": 4,
        "T": 4
    }
    now = time.time()  
    nowoffset = now + 3600*offset[server]
    dayoffset = nowoffset - nowoffset%86400
    day = dayoffset - 3600*offset[server]
    return int(day)*10**9

async def history_today(group_id: str):
    """
    今天已出的刀
    """
    today = get_today_start_time(await group_server(group_id))
    history = await dbclient.execute_fetchall("SELECT * FROM purikone_clanbattle_history WHERE groupid=? AND date>?", (group_id, today))
    _all = len(history)
    _full = len([i for i in history if i[6]==0 and i[7]==0])  # 完整刀
    _end = len([i for i in history if i[6]==1 and i[7]==0])  # 未完成的尾刀
    _compensiate = len([i for i in history if i[7]==1])  # 已结算的尾刀
    return _all, _full, _end, _compensiate
    
async def reserve_boss(group_id: str, user_id: str, boss_id: int, nickname: str = "", turn: int = 0, notes: str = ""):
    """
    预约出刀
    """
    await dbclient.execute("INSERT INTO purikone_clanbattle_reserve VALUES (?,?,?,?,?);", (group_id, (nickname or user_id), turn, boss_id, notes))
    await dbclient.commit()
    return 

async def cancel_reserve(group_id: str, user_id: str = None, boss_id: int = None):
    """
    取消预约
    """
    if user_id and boss_id:
        await dbclient.execute("DELETE FROM purikone_clanbattle_reserve WHERE groupid=? AND user=? AND bossid=?;", (group_id, user_id, boss_id))
        await dbclient.commit()
        return True
    elif user_id:
        await dbclient.execute("DELETE FROM purikone_clanbattle_reserve WHERE groupid=? AND user=?;", (group_id, user_id))
        await dbclient.commit()
        return True
    elif boss_id:
        await dbclient.execute("DELETE FROM purikone_clanbattle_reserve WHERE gouprid=? AMD boss=?;", (group_id, boss_id))
        await dbclient.commit()
        return True
    return False

async def get_reserve(group_id: str, boss_id: int = 0):
    """
    查询预约表
    """
    if boss_id in range(1,6):
        _r = await dbclient.execute_fetchall("SELECT * FROM purikone_clanbattle_reserve WHERE groupid=? AND bossid=?", (group_id, boss_id))
        return list(_r)
    elif not boss_id:
        _r = await dbclient.execute_fetchall("SELECT * FROM purikone_clanbattle_reserve WHERE groupid=?", (group_id, ))
        return list(_r)
    else:
        return None