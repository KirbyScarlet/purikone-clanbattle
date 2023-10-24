###

from nonebot import on_shell_command
from nonebot.rule import ArgumentParser

report_args = ArgumentParser()
report_args.add_argument("n", type=str, default="0", dest="n", help="报刀几王")
report_args.add_argument("damage", type=str, default="0", dest="damage", help="伤害值")
report_args.add_argument("b", "补", action="store_true", dest="b", help="是否是补偿刀")
report_args.add_argument("撤销", action="store_true", dest="cancel", help="撤销最近一次报刀")

REPORT_HELP = """\
报刀 [几王] [伤害] [补]

"""
