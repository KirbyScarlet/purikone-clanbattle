##

from nonebot import on_shell_command
from nonebot.rule import ArgumentParser

from nonebot.adapters import Bot, Event
from nonebot.params import ShellCommandArgs

try:
    from nonebot.adapters.onebot.v11 import Event as Eventv11
    from nonebot.adapters.onebot.v11 import MessageSegment as MessageSegmentv11
except ImportError:
    Eventv11 = None
    MessageSegmentv11 = None

from argparse import Namespace

modify_args = ArgumentParser()
modify_args.add_argument("args", nargs="*", type=str, dest="args", )