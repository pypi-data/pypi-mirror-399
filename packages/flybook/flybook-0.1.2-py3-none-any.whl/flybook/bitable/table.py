import httpx

from .bitable import Bitable
from ..common import checkFeishuResponse, COMMON_HEADER


class Table:
    def __init__(self, bitable: Bitable, id: str):
        self.bitable = bitable
        self.id = id

    def add_record(self, access_token: str, fields: dict,
                   user_id_type: str | None = None):
        """
            添加记录

            :param access_token: 飞书机器人访问令牌
            :param fields: 记录字段
            :param user_id_type: 用户ID类型，需与Record中的用户ID类型一致
        """
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.bitable.app_token}/tables/{self.id}/records"
        headers = {
            **COMMON_HEADER,
            "Authorization": f"Bearer {access_token}"
        }
        params = {}
        if user_id_type:
            params['user_id_type'] = user_id_type
        response = httpx.post(url, headers=headers, params=params,
                              json={"fields": fields})
        response = checkFeishuResponse(response)
        return response["data"]["record"]["id"]

    def update_record(self, access_token: str, record_id: str, fields: dict,
                      user_id_type: str | None = None):
        """
            更新记录

            :param access_token: 飞书机器人访问令牌
            :param record_id: 记录ID
            :param fields: 记录字段
            :param user_id_type: 用户ID类型，需与Record中的用户ID类型一致
        """
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.bitable.app_token}/tables/{self.id}/records/{record_id}"
        headers = {
            **COMMON_HEADER,
            "Authorization": f"Bearer {access_token}"
        }
        params = {}
        if user_id_type:
            params['user_id_type'] = user_id_type
        response = httpx.put(url, headers=headers, params=params,
                             json={"fields": fields})
        checkFeishuResponse(response)
