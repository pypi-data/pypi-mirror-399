import httpx
import hashlib
from base64 import b64encode
from time import time
import hmac

from .common import COMMON_HEADER, checkFeishuResponse
from .message import Message


class CustomBot:
    """
        飞书自定义机器人接口
        参考文档: https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot

        :param webhook: 自定义机器人的webhook地址
        :param secret?: 自定义机器人的secret, 用于签名验证, 默认为None
    """

    def __init__(self, webhook: str, secret: str | None = None):
        self.webhook = webhook
        self.secret = secret

    def send_message(self, message: Message):
        """
            发送自定义内容到飞书自定义机器人

            :param message: 要发送的消息, 必须是一个字典，格式参考官方文档
        """
        message = self._prepare(message)
        response = httpx.post(self.webhook, json=message,
                              headers=COMMON_HEADER)
        checkFeishuResponse(response)

    def _prepare(self, message: Message) -> dict:
        if message.type == "post":
            raise NotImplementedError("自定义机器人不支持发送Markdown消息")
        message = {"msg_type": message.type,
                   message.key: message.data}
        if self.secret:
            timestamp = int(time())
            sign = f"{timestamp}\n{self.secret}"
            sign = hmac.new(
                sign.encode("utf-8"),
                digestmod=hashlib.sha256).digest()
            sign = b64encode(sign).decode("utf-8")
            message['timestamp'] = timestamp
            message['sign'] = sign
        return message
