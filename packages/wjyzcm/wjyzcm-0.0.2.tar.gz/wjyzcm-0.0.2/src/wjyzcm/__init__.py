from nonebot import get_plugin_config, on_command
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="wjyzcm",
    description="万静怡",
    usage="使用方式:"
          "    wjy"
          "    zcm",
    config=Config,
)

config = get_plugin_config(Config)

wjy = on_command(cmd='wjy')


@wjy.handle()
async def handle_function(bot: Bot, event: Event):
    message = "zcm"
    await wjy.finish(message)
