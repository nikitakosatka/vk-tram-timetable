import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from key import token


def send_message(user_id, message):
    session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0})


session = vk_api.VkApi(token=token)
session_api = session.get_api()
long_poll = VkLongPoll(session)

for event in long_poll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            message = event.text
            user_id = event.user_id
