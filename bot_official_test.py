# 公主连结团队战机器人
# 官方bot版

import nonebot
from nonebot.adapters.qq import Bot, Event, MessageEvent
from nonebot.adapters.qq import Adapter as AdapterQQOfficial

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(AdapterQQOfficial)

from nonebot import on_command
from nonebot.adapters.qq import MessageSegment

test = on_command("test")

@test.handle()
async def _test(bot: Bot, event: MessageEvent):
    m = await bot.post_group_members(group_id=event.group_id)
    nonebot.logger.info(str(m))
    await test.finish(MessageSegment.text("测试成功"))

if __name__ == "__main__":
    nonebot.run(host="0.0.0.0")