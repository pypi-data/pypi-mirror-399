import pytest
from os import getenv
from dotenv import load_dotenv
from datetime import datetime
from uuid import uuid4

from flybook.bot import Bot
from flybook.user import User
from flybook.bitable import Bitable, Table

load_dotenv(".env.test")


class TestBitable:
    def setup_method(self):
        app_id = getenv("BOT_APP_ID")
        app_secret = getenv("BOT_APP_SECRET")
        self.bot = Bot(app_id, app_secret)
        self.bitable = Bitable(app_token=getenv("BITABLE_APP_TOKEN"))
        self.table = Table(self.bitable, getenv("BITABLE_TABLE_ID"))

    def test_add_record(self):
        group = getenv("GROUP_ID")
        user = User(getenv("USER_ID"))
        fields = {
            "文本": "测试记录",
            "数字": 123.456,
            "单选": "good",
            "多选": ["a", "b", "d"],
            "日期": datetime.now().timestamp() * 1000,
            "复选框": True,
            "群组": [{"id": group}],
            "人员": [{"id": user.id}],
            "超链接": {
                "text": "飞书多维表格官网",
                "link": "https://www.feishu.cn/product/base"
            },
        }
        self.table.add_record(self.bot.tenant_access_token,
                              fields,
                              user.type)

    def test_update_record(self):
        record_id = getenv("BITABLE_RECORD_ID")
        fields = {
            "文本": str(uuid4()),
        }
        self.table.update_record(self.bot.tenant_access_token,
                                 record_id,
                                 fields)

    def test_get_records(self):
        self.table.get_records(self.bot.tenant_access_token,
                               "文本", "测试记录", ["文本"])
