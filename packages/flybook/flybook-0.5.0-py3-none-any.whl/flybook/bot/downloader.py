import httpx
import json

from .prototype import BotPrototype


class Downloader(BotPrototype):
    """
        飞书文件下载类
    """

    def download_media(self, token: str):
        """
            下载飞书文件

            :param token: 素材token
        """
        url = f"https://open.feishu.cn/open-apis/drive/v1/medias/{token}/download"
        headers = {
            'Authorization': f'Bearer {self.tenant_access_token}'
        }
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        return response.content
