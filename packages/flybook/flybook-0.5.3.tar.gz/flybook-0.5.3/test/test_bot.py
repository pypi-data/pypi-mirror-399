import pytest
from os import getenv
from dotenv import load_dotenv

from flybook.bot import Bot
from flybook.user import User
from flybook.message import MarkdownMessage, SimpleCardMessage, TextMessage

load_dotenv(".env.test")


class TestMessageSender:
    def setup_method(self):
        app_id = getenv("BOT_APP_ID")
        app_secret = getenv("BOT_APP_SECRET")
        self.bot = Bot(app_id, app_secret)

    def test_send_text_message(self):
        tenant_access_token = getenv("BOT_TENANT_ACCESS_TOKEN")
        receiver = User(getenv("USER_ID"))
        message = TextMessage("Hello, World!")
        self.bot.send_message(receiver, message)

    def test_send_card_message(self):
        receiver = User(getenv("GROUP_ID"))
        card = SimpleCardMessage("你好！", "**世界**", "orange")
        self.bot.send_message(receiver, card)


class TestDownloader:
    def setup_method(self):
        app_id = getenv("BOT_APP_ID")
        app_secret = getenv("BOT_APP_SECRET")
        self.bot = Bot(app_id, app_secret)

    def test_download_file(self):
        token = getenv("MEDIA_TOKEN")
        content = self.bot.download_media(token)
        assert content.decode("utf-8").startswith("# generated using pymatgen")


class TestMessageRelier:
    def setup_method(self):
        app_id = getenv("BOT_APP_ID")
        app_secret = getenv("BOT_APP_SECRET")
        self.bot = Bot(app_id, app_secret)

    def test_reply_markdown_message(self):
        user_id = getenv("USER_ID")
        message_id = getenv("MESSAGE_ID")
        message = MarkdownMessage(f"你好，<at user_id=\"{user_id}\"></at>")
        self.bot.reply_message(message_id, message)

    def test_reply_card_message(self):
        message_id = getenv("MESSAGE_ID")
        message = SimpleCardMessage(None, "**世界**", "orange")
        self.bot.reply_message(message_id, message)
