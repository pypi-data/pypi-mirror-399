from datetime import datetime

from ..common import COMMON_HEADER, checkFeishuResponse
from .prototype import BotPrototype
from .messageSender import MessageSender
from .downloader import Downloader
from .messageRelier import MessageRelier


class Bot(MessageSender, Downloader, MessageRelier):
    """
        飞书机器人类
    """
