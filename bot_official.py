# 公主连结团队战机器人
# 官方bot版

import nonebot
from nonebot.adapters.qq import Adapter as AdapterQQOfficial

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(AdapterQQOfficial)

nonebot.load_plugin("nonebot_plugin_purikone_clanbattle")

if __name__ == "__main__":
    nonebot.run(host="0.0.0.0", port=65008)