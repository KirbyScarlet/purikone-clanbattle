# OnebotV11适配

__all__ = [
    "_apply",
    "_create",
    "_user",
]

import nonebot
from nonebot.rule import Rule
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.params import CommandArg
from nonebot import on_command, on_message
from nonebot.message import event_preprocessor
from nonebot.typing import T_State
from nonebot.log import logger

from . import purikone_clanbattle as pcr

@event_preprocessor
async def _(event: MessageEvent, state: T_State):
    state["group_id"] = event.group_id
    state["user_id"] = event.sender.user_id
    # logger.info(event.json())

async def build_message(res: list[dict]) -> Message:
    m = Message()
    for d in res:
        for k, v in d.items():
            m += MessageSegment.__getattribute__(MessageSegment, k).__func__(MessageSegment, v)
    return m

async def check_group_clanbattle_start(event: MessageEvent, matcher: Matcher, state: T_State):
    server, _ = await pcr.utils.sqliteapi.group_check(state["group_id"])
    if not server:
        await matcher.finish("""\
该群未创建会战，请管理员执行以下命令
命令格式：
  @机器人 会战开始""")
    
apply = on_command("申请出刀")

@apply.handle()
async def _apply(bot: Bot, event: Event, matcher: Matcher, state: T_State, msg: Message = CommandArg()):
    await check_group_clanbattle_start(event, apply, state)
    arg = await pcr.apply.apply_parser(msg)
    if arg is None:
        await apply.finish("请检查命令格式\n" + pcr.apply.APPLY_HELP)
    res = await pcr.apply.apply(state["group_id"], state["user_id"], arg)
    await apply.finish(await build_message(res))

apply_simple = on_command("进")

@apply_simple.handle()
async def _apply_simple(bot: Bot, event: Event, matcher: Matcher, state: T_State, msg: Message = CommandArg()):
    await check_group_clanbattle_start(event, apply_simple, state)
    arg = await pcr.apply.apply_parser(msg)
    if arg is None:
        await apply_simple.finish()
    res = await pcr.apply.apply(state["group_id"], state["user_id"], arg)
    await apply_simple.finish(await build_message(res))

create = on_command("会战开始")

@create.handle()
async def _create(bot: Bot, event: Event, matcher: Matcher, state: T_State, msg: Message = CommandArg()):
    arg = await pcr.create.create_parser(msg)
    if arg is None:
        await create.finish("请检查命令格式\n" + pcr.create.CREATE_HELP)
    res = await pcr.create.create(state["group_id"], arg)
    await create.finish(await build_message(res))

user = on_command("加入行会")

@user.handle()
async def _user(bot: Bot, event: Event, matcher: Matcher, state: T_State, msg: Message = CommandArg()):
    await check_group_clanbattle_start(event, user, state)
    arg = await pcr.user.user_parser(msg)
    if arg is None:
        await user.finish("请指定一个自己的昵称\n  @机器人 加入行会 昵称")
    res = await pcr.user.user_add(state["group_id"], state["user_id"], arg)
    await user.finish(await build_message(res))

hedao = on_command("合刀")

@hedao.handle()
async def _hedao(bot: Bot, event: Event, matcher: Matcher, state: T_State, msg: Message = CommandArg()):
    a, b, c = await pcr.hedao.hedao_parser(msg)
    if not a:
        await hedao.finish(pcr.hedao.HEDAO_HELP)
    res = await pcr.hedao.hedao(a, b, c)
    await hedao.finish(await build_message(res))

report = on_command("报刀")
end_report = on_command("尾刀")

@report.handle()
async def _report(bot: Bot, event: Event, state: T_State, msg: Message = CommandArg()): #, args: Namespace = ShellCommandArgs()):
    await check_group_clanbattle_start(event, user, state)
    arg = await pcr.report.report_parser(msg)
    if arg is None:
        await report.finish("请检查命令格式\n" + pcr.report.REPORT_HELP)
    res = await pcr.report.report(state["group_id"], state["user_id"], arg)
    await report.finish(await build_message(res))

@end_report.handle()
async def _end_report(bot: Bot, event: Event, state: T_State, msg: Message = CommandArg()):
    await check_group_clanbattle_start(event, user, state)
    arg = await pcr.report.end_report_parser(msg)
    if arg is None:
        await end_report.finish("请检查命令格式\n" + pcr.report.REPORT_HELP)
    res = await pcr.report.end_report(state["group_id"], state["user_id"], arg)
    await end_report.finish(await build_message(res))

status = on_command("状态", aliases={"进度"})

@status.handle()
async def _status(bot: Bot, event: Event, state: T_State, msg: Message = CommandArg()):
    await check_group_clanbattle_start(event, user, state)
    if len(msg) > 0:
        await status.finish()
    else:
        res = await pcr.status.status(state["group_id"])
        print(res)
        await status.finish(await build_message(res))

tree = on_command("挂树")
cancel_tree = on_command("下树", aliases={"取消挂树"})

@tree.handle()
async def _tree(bot: Bot, event: Event, state: T_State, msg: Message = CommandArg()):
    await check_group_clanbattle_start(event, user, state)
    m = msg.extract_plain_text()
    res = await pcr.tree.tree(state["group_id"], state["user_id"], m)
    await tree.finish(await build_message(res))

@cancel_tree.handle()
async def _cancel_tree(bot: Bot, event: Event, state: T_State, msg: Message = CommandArg()):
    res = await pcr.tree.christmas_tree(state["group_id"], state["user_id"])
    await cancel_tree.finish(await build_message(res))

modify = on_command("修改")

@modify.handle()
async def _modify(bot: Bot, event: Event, state: T_State, msg: Message = CommandArg()):
    await check_group_clanbattle_start(event, user, state)
    args = await pcr.modify.modify_parser(msg)
    if args.error:
        await modify.finish(await build_message(args.error))
    res = await pcr.modify.modify(state["group_id"], args)
    await modify.finish(await build_message(res))

reserve = on_command("预约")

@reserve.handle()
async def _reserve(bot: Bot, event: Event, state: T_State, msg: Message = CommandArg()):
    await check_group_clanbattle_start(event, user, state)
    args = await pcr.reserve.reserve_parser(msg)
    if not args:
        await reserve.finish(pcr.reserve.RESERVE_HELP)
    await reserve.finish(str(args))

test = on_command("测试", aliases={"test"})
@test.handle()
async def _test(bot: Bot, event: Event, state: T_State, msg: Message = CommandArg()):
    await test.finish(MessageSegment.at(event.sender.user_id)+MessageSegment.text(" ciallo~"))
                
