from .prototype import Message


class CardMessage(Message):
    """
        卡片消息

        :param data: 消息卡片的原始字典数据
    """
    type = "interactive"
    key = "card"

    def __init__(self, data: dict):
        self._data = data

    @property
    def data(self) -> dict:
        """
            获取消息卡片的原始字典数据

            :return: 消息卡片的原始字典数据
        """
        return self._data


class TemplateCardMessage(CardMessage):
    """
        基于模板的飞书卡片消息

        :param id: 消息卡片的模板ID
        :param version: 消息卡片的模板版本
        :param variables?: 消息卡片的模板参数，默认为空字典
    """

    def __init__(self, id: str, version: str, variable: dict | None = None):
        self.id = id
        self.version = version
        self.variable = variable or {}

    @property
    def data(self) -> dict:
        """
            获取消息卡片的原始字典数据

            :return: 消息卡片的原始字典数据
        """
        return {
            "type": "template",
            "data": {
                "template_id": self.id,
                "template_version_name": self.version,
                "template_variable": self.variable
            }
        }


class SimpleCardMessage(CardMessage):
    """
        简单的飞书卡片消息

        :param title: 卡片的标题
        :param text: 卡片的文本内容
    """

    def __init__(self, title: str, content: str, titleColor: str = "blue"):
        self.title = title
        self.content = content
        self.titleColor = titleColor

    @property
    def data(self) -> dict:
        """
            获取消息卡片的原始字典数据

            :return: 消息卡片的原始字典数据
        """
        data = {
            "schema": "2.0",
            "header": {
                "title": {
                    "tag": "lark_md",
                    "content": self.title
                },
                "template": self.titleColor
            },
            "body": {
                "elements": [
                    {
                        "tag": "markdown",
                        "content": self.content
                    }
                ]
            }
        }
        return data
