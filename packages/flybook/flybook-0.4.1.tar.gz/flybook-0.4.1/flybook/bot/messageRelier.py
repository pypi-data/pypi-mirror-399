import httpx
from json import dumps

from ..common import COMMON_HEADER, checkFeishuResponse
from .prototype import BotPrototype
from ..user import User
from ..message import Message


class MessageRelier(BotPrototype):
    """
        飞书消息回复类
    """

    def reply_message(self, message_id: str, message: Message, in_thread: bool = False):
        """
            回复消息到飞书机器人

            :param message_id: 消息ID
            :param message: 消息对象
            :param in_thread: 是否在话题中回复，默认为False
        """
        url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply"
        payload = {
            "content": dumps(message.data),
            "msg_type": message.type,
            "reply_in_thread": in_thread
        }
        headers = {
            **COMMON_HEADER,
            'Authorization': f'Bearer {self.tenant_access_token}'
        }
        response = httpx.post(url, headers=headers, json=payload)
        checkFeishuResponse(response)
