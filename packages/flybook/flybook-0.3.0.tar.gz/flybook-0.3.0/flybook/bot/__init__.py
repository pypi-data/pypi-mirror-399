from datetime import datetime

from ..common import COMMON_HEADER, checkFeishuResponse
from .prototype import BotPrototype
from .messageSender import MessageSender
from .downloader import Downloader


class Bot(MessageSender, Downloader):
    """
        飞书机器人类
    """
