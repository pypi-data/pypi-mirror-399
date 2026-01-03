import httpx


COMMON_HEADER = {
    'Content-Type': 'application/json; charset=utf-8'
}


class FeishuAPIException(Exception):
    """
        飞书API异常
    """


def checkFeishuResponse(response: httpx.Response):
    """
        检查飞书API响应是否成功
    """
    try:
        response.raise_for_status()
    except:
        raise FeishuAPIException(response.text)
    response = response.json()
    if response['code'] != 0:
        raise FeishuAPIException(response)
    return response
