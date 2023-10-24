### 报刀

from nonebot import on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.adapters import Bot, Event, Message
from nonebot.params import ShellCommandArgs, CommandArg
from argparse import Namespace
from nonebot.log import logger

from nonebot.adapters.satori import MessageEvent as MessageEventSatori

from .utils import check_bot
#from .utils import sint

# 有问题，暂时弃用
#report_args = ArgumentParser()
#report_args.add_argument("n", type=int, nargs="?", choices=range(1,6), help="报刀几王")
#report_args.add_argument("damage", type=str, default="0", help="伤害值")
#report_args.add_argument("extra", type=str, nargs="?", choices=("b","补"), help="是否是补偿刀")

end_report_args = ArgumentParser()
end_report_args.add_argument("extra", type=str, nargs="?", choices=("b","补"), help="是否是补偿刀")

REPORT_HELP = """\
报刀 [几王] [伤害|尾刀] [补] [撤销]
尾刀 [补]
"""

report = on_shell_command("报刀", rule=check_bot)
end_report = on_shell_command("尾刀", parser=end_report_args, rule=check_bot)

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


@report.handle()
async def _handle_report(bot: Bot, event: Event, msg: Message = CommandArg()): #, args: Namespace = ShellCommandArgs()):
    args = await report_parser(msg)
    if isinstance(event, MessageEventSatori):
        user_id = event.user.id


@end_report.handle()
async def _handle_end_report(bot: Bot, event: Event, args: Namespace = ShellCommandArgs()):
    await end_report.finish("#尾刀\n"+str(args))

