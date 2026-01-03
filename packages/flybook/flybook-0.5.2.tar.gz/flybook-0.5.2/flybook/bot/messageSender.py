import httpx
from json import dumps

from ..common import COMMON_HEADER, checkFeishuResponse
from .prototype import BotPrototype
from ..user import User
from ..message import Message


class MessageSender(BotPrototype):
    """
        飞书消息发送类
    """

    def send_message(self, receiver: User,  message: Message):
        """
            发送消息到飞书机器人

            :param receiver: 接收者对象
            :param msg_type: 消息类型
            :param content: 消息内容
        """
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        message = {
            'receive_id': receiver.id,
            'msg_type': message.type,
            'content': dumps(message.data)
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
