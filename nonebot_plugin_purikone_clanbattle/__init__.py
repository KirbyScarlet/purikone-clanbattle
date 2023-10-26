from nonebot.plugin import PluginMetadata
from nonebot import get_driver

__plugin_meta__ = PluginMetadata(
    name="公主连结会战",
    description="",
    usage='''\


''',
)

from .status import _handle_status
from .calc import _pair
from .reserve import _reservation
from .report import _handle_report, _handle_end_report
from .apply import _handle_apply
from .tree import _handle_tree, _handle_check_tree, _handle_cancel_tree
from .settings import _handle_settings
from .create import _create

from .utils import dbclient

@get_driver().on_shutdown
async def _():
    await dbclient.close()