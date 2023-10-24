from nonebot.plugin import PluginMetadata
from nonebot import get_driver

__plugin_meta__ = PluginMetadata(
    name="公主连结会战",
    description="",
    usage='''\


''',
)

from .calc import _pair
from .reserve import _reservation
from .report import _handle_report, _handle_end_report
from .apply import _apply
from .tree import _tree, _check_tree, _cancel_tree
from .settings import _handle_settings
from .create import _create
from .status import _handle_status

from .utils import dbclient

@get_driver().on_shutdown
async def _():
    await dbclient.close()