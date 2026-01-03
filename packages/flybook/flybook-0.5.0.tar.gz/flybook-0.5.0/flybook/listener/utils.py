from collections import namedtuple
from json import loads
from ..user import User


async def parseMessage(request, logger):
    body = await request.json()
    logger.info(f"{request.method} {request.url.path}: {body}")
    if not body["header"]["event_type"] == "im.message.receive_v1":
        return
    message_id = body["event"]["message"]["message_id"]
    sender_id = body["event"]["sender"]["sender_id"]["union_id"]
    mentions_id = body['event']['message']['mentions']
    sender = User(sender_id)
    mentions = {mention["key"]: User(mention['id']['union_id'])
                for mention in mentions_id}
    return namedtuple('Message', ['id', 'sender', 'mentions'])(message_id, sender, mentions)
