"""词汇审查插件配置模块。

定义了插件所需的配置项，通过 NoneBot 的全局配置加载。
"""

from pathlib import Path

from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    """插件配置模型。

    Attributes:
        send_word_blacklist_file: 黑名单存储文件的路径 (JSON 格式)。
        send_word_priority: 插件的事件响应优先级。
    """

    send_word_blacklist_file: Path = Path("./src/send_word_blacklist.json")
    send_word_priority: int = 100


# 加载插件配置
plugin_config = get_plugin_config(Config)