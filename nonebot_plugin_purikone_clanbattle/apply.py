# 申请出刀

from nonebot import on_shell_command, on_command
from nonebot.rule import ArgumentParser
from nonebot.adapters import Bot, Event, Message
from nonebot.params import ShellCommandArgs, CommandArg
from argparse import Namespace

from .utils import check_bot

apply = on_command("申请出刀", aliases={"进", "进刀"}, rule=check_bot)

async def apply_parser(msg):
    m = "".join(msg.split())
    if len(m) == 1:
        if m in "12345":
            return Namespace(n=m, b=False)
    if len(m) == 2:
        if m[0] in "12345" and m[1] in "b补":
            return Namespace(n=m[0], b=True)
    return None    

@apply.handle()
async def _apply(bot: Bot, event: Event, msg: Message = CommandArg()):
    args = await apply_parser(msg)
    await apply.finish("#申请出刀\n"+str(args))
    if not args:
        await apply.finish("请检查申请参数")