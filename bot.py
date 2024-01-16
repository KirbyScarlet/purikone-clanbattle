# 公主连结团队战机器人

import nonebot

from nonebot.adapters.onebot.v11 import Adapter as AdapterV11

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(AdapterV11)

nonebot.load_plugin("nonebot_plugin_purikone_clanbattle")

if __name__ == "__main__":
    nonebot.run()