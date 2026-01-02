import lark_oapi as lark
import httpx


class Listener:
    """
        飞书事件和回调监听器

        :param app_id: 飞书应用ID
        :param app_secret: 飞书应用密钥
        :param endpoint: 回调URL
        :param headers?: 自定义请求头，默认{"Content-Type": "application/json"}
        :param log_level?: 日志级别，默认INFO
    """

    def __init__(self, app_id: str, app_secret: str,
                 endpoint: str, headers: dict = None,
                 log_level: lark.LogLevel = lark.LogLevel.INFO):
        if headers is None:
            headers = {"Content-Type": "application/json"}

        def handler(data):
            data = lark.JSON.marshal(data)
            httpx.post(endpoint, json=data, headers=headers)

        handler = lark.EventDispatcherHandler.builder("", "") \
            .register_p2_im_message_receive_v1(handler) \
            .build()

        self.client = lark.ws.Client(app_id, app_secret,
                                     event_handler=handler,
                                     log_level=log_level)

    def __call__(self):
        self.client.start()
