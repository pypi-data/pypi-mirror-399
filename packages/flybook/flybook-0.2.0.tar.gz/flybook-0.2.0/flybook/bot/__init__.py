from datetime import datetime

from ..common import COMMON_HEADER, checkFeishuResponse
from .prototype import BotPrototype
from .messageSender import MessageSender


class Bot(MessageSender):
    """
        飞书机器人类
    """
