class User:
    """
        用户类

        :param id: 用户ID
    """

    def __init__(self, id: str):
        self.id = id

    @property
    def type(self):
        if self.id.startswith('oc_'):
            return 'chat_id'
        elif self.id.startswith('on_'):
            return 'union_id'
        elif self.id.startswith('ou_'):
            return 'open_id'
        return 'user_id'
