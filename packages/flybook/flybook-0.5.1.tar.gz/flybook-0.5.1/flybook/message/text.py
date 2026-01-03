from .prototype import Message


class TextMessage(Message):
    """
        文本消息

        :param data: 文本消息的内容
    """
    type = "text"
    key = "content"

    def __init__(self, data: str):
        self._data = data

    @property
    def data(self):
        return {"text": self._data}
