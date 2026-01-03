from .prototype import Message


class MarkdownMessage(Message):
    """
        Markdown消息

        :param data: Markdown消息的内容
    """
    type = "post"
    key = "content"

    def __init__(self, markdown: str, title: str = None):
        self._data = markdown
        self.title = title

    @property
    def data(self):
        return {
            "zh_cn": {
                "title": self.title,
                "content": [
                    [
                        {
                            "tag": "md",
                            "text": self._data
                        }
                    ]
                ]
            }
        }
