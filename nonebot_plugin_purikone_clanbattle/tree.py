## 挂树

from nonebot import on_shell_command, on_command
from nonebot.rule import ArgumentParser
from nonebot.adapters import Bot, Event, Message
from nonebot.params import ShellCommandArgs, CommandArg
from argparse import Namespace

from .utils import check_bot

tree = on_command("挂树", rule=check_bot)
check_tree = on_command("查树", rule=check_bot)
cancel_tree = on_command("下树", aliases={"取消挂树"}, rule=check_bot)

@tree.handle()
async def _tree(bot: Bot, event: Event, msg: Message = CommandArg()):
    m = msg.extract_plain_text()
    await tree.finish("#挂树" + str(m))

@check_tree.handle()
async def _check_tree(bot: Bot, event: Event, msg: Message = CommandArg()):
    m = msg.extract_plain_text()
    await check_tree.finish("#查树" + str(m))

@cancel_tree.handle()
async def _cancel_tree(bot: Bot, event: Event, msg: Message = CommandArg()):
    m = msg.extract_plain_text()
    await cancel_tree.finish("#下树")