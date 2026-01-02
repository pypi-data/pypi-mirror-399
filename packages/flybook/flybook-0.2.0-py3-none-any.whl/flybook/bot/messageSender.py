import httpx
import json

from ..common import COMMON_HEADER, checkFeishuResponse
from .prototype import BotPrototype
from ..messageCard import MessageCard
from ..user import User


class MessageSender(BotPrototype):
    """
        飞书消息发送类
    """

    def send_message(self, receiver: User,
                     msg_type: str, content: dict):
        """
            发送消息到飞书机器人

            :param receiver: 接收者对象
            :param msg_type: 消息类型
            :param content: 消息内容
        """
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        message = {
            'receive_id': receiver.id,
            'msg_type': msg_type,
            'content': json.dumps(content)
        }
        headers = {
            **COMMON_HEADER,
            'Authorization': f'Bearer {self.tenant_access_token}'
        }
        response = httpx.post(
            url,
            headers=headers,
            json=message,
            params={'receive_id_type': receiver.type}
        )
        checkFeishuResponse(response)

    def send_text_message(self, receiver: User, text: str):
        """
            发送文本消息到飞书机器人

            :param receiver: 接收者对象
            :param text: 文本内容
        """
        self.send_message(receiver, 'text', {'text': text})

    def send_card_message(self, receiver: User, card: MessageCard):
        """
            发送卡片消息到飞书机器人

            :param receiver: 接收者对象
            :param card: 卡片内容
        """
        self.send_message(receiver, 'interactive', card.cardData)
