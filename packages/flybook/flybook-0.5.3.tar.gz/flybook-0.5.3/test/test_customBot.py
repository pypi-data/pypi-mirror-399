import pytest
from os import getenv
from dotenv import load_dotenv

from flybook.customBot import CustomBot
from flybook.message import TextMessage, TemplateCardMessage, SimpleCardMessage, MarkdownMessage

load_dotenv(".env.test")


class TestCustomBot:
    """Test cases for the CustomBot class"""

    def setup_method(self):
        public = getenv("CUSTOM_BOT_PUBLIC")
        webhook = getenv("CUSTOM_BOT_WEBHOOK")
        secret = getenv("CUSTOM_BOT_SECRET")
        self.public_bot = CustomBot(public)
        self.secret_bot = CustomBot(webhook, secret)

    def test_send_text(self):
        self.public_bot.send_message(TextMessage("你好，世界！"))

    def test_send_simple_card(self):
        card = SimpleCardMessage("你好！", "**世界**", "orange")
        self.public_bot.send_message(card)

    def test_send_template_card(self):
        template_id = getenv("MESSAGE_CARD_TEMPLATE_ID")
        template_version = getenv("MESSAGE_CARD_TEMPLATE_VERSION")
        variable = {
            "title": "你好！",
            "content": "**世界**"
        }
        card = TemplateCardMessage(template_id, template_version, variable)
        self.secret_bot.send_message(card)
