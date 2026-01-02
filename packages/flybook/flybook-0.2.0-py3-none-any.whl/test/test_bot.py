import pytest
from os import getenv
from dotenv import load_dotenv

from flybook.bot import Bot
from flybook.user import User
from flybook.messageCard import SimpleMessageCard

load_dotenv(".env.test")


class TestMessageSender:
    def setup_method(self):
        app_id = getenv("BOT_APP_ID")
        app_secret = getenv("BOT_APP_SECRET")
        self.bot = Bot(app_id, app_secret)

    def test_send_text_message(self):
        tenant_access_token = getenv("BOT_TENANT_ACCESS_TOKEN")
        receiver = User(getenv("USER_ID"))
        self.bot.send_text_message(receiver, "Hello, World!")

    def test_send_card_message(self):
        receiver = User(getenv("GROUP_ID"))
        card = SimpleMessageCard("你好！", "**世界**", "orange")
        self.bot.send_card_message(receiver, card)
