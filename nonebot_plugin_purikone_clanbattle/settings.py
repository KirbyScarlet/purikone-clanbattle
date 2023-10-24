###

from nonebot import on_shell_command, on_command
from nonebot.rule import ArgumentParser

from nonebot.adapters import Bot, Event, Message
from nonebot.params import ShellCommandArgs, CommandArg
from nonebot.log import logger

try:
    from nonebot.adapters.onebot.v11 import Event as Eventv11
    from nonebot.adapters.onebot.v11 import MessageSegment as MessageSegmentv11
except ImportError:
    Eventv11 = None
    MessageSegmentv11 = None

from argparse import Namespace

from .utils import check_bot, dbclient, sint

# 有问题，先不用这个，后面再改
#settings_args = ArgumentParser()
#settings_args.add_argument("阶段","阶段数", type=int, dest="turn", help="设定每个阶段的第一个周目，跟几个数字就有几个阶段")
#settings_args.add_argument("血量", nargs="*", type=str, dest="maxhp", help="修改boss最大血量")

SETTINGS_ARGS_HELP = """\
设定 阶段 a1 b4 c11 d31 e41
设定 血量 a1 600w a2 800w a3 1000w a4 1100w a5 1200w ... """

settings = on_command("设置", rule=check_bot)

async def _settings_parser(msg: Message):
    m = msg.extract_plain_text().split()
    if m[0] == "阶段":
        return Namespace(turn=m[1:], maxhp=None)
    if m[0] == "血量":
        return Namespace(maxhp=m[1:], turn=None)
    return None
    

@settings.handle()
async def _handle_settings(bot: Bot, event: Event, msg: Message = CommandArg()):
    args = await _settings_parser(msg)
    #await settings.send("#设置\n"+str(args))
    res = await _settings(args)
    await settings.finish(res)

def _turn_check(t: str):
    try:
        chapter = t[0]
        turn = int(t[1:])
    except:
        return None
    return chapter, turn

def _maxhp_check(bossandhp: list):
    if len(bossandhp)%2:
        return None
    res = []
    for i in range(0, len(bossandhp), 2):
        try:
            res.append((bossandhp[i][0], f"boss{int(bossandhp[i][1])}", sint(bossandhp[i+1])))
        except:
            res.append(None)
            break
    return res

async def _settings(args: Namespace):
    if args.turn:
        _t = [_turn_check(t) for t in args.turn]
        if None in _t:
            return "参数设置错误"
        for t in _t:
            await dbclient.execute("INSERT INTO purikone_clanbattle_settings (chapter, turn) VALUES (?,?)", t)
            await dbclient.commit()
        return "阶段设置成功"
    if args.maxhp:
        _m = _maxhp_check(args.maxhp)
        if None in _m:
            return "参数设置错误"
        for m in _m:
            try:
                await dbclient.execute(f"UPDATE purikone_clanbattle_settings SET {m[1]} = {str(m[2].value)} WHERE chapter = '{m[0]}'")
            except Exception as e:
                logger.error(e)
            await dbclient.commit()
        return "最大血量设置成功"