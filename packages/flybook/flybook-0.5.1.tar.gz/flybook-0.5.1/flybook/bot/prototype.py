import httpx

from ..common import COMMON_HEADER, checkFeishuResponse


class BotPrototype:
    """
        飞书机器人原型类

        :param app_id: 飞书应用ID
        :param app_secret: 飞书应用密钥
    """

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_access_token = ""
        self.get_tenant_access_token()

    def get_tenant_access_token(self):
        """
            获取飞书租户访问令牌
        """
        response = httpx.post(
            'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/',
            json={
                'app_id': self.app_id,
                'app_secret': self.app_secret
            }
        )
        response = checkFeishuResponse(response)
        self.tenant_access_token = response['tenant_access_token']
