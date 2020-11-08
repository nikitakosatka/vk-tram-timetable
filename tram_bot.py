import vk_api
import json
import requests
from bs4 import BeautifulSoup as bs
from vk_api.longpoll import VkLongPoll, VkEventType


def get_routes():
    tram_routes = {}

    r = requests.get('https://www.24tr.ru/magnitogorsk/tramvay/')
    html = bs(r.content, 'html.parser')

    for element in html.select('.numbithem'):
        tram_routes[element.select('.numit2 > a')[0].text] = \
            element.select('.numit2 > a')[0].get('href')

    return tram_routes


def str_dict(dct):
    result = ''
    for i in dct:
        result += str(i) + ', '

    return result[:-2]


def get_button(text, colour):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{colour}"
    }


def get_timetable(route_href):
    result = ''

    r = requests.get('https://www.24tr.ru' + route_href)
    html = bs(r.content, 'html.parser')

    ways = [i.text for i in html.select('.dker > span')]

    for i in html.select('.font-schedule'):
        result += ways.pop(0) + '\n' + i.text + '\n\n'

    return result


class TramBot:
    def __init__(self, token):
        self.session = vk_api.VkApi(token=token)
        self.session_api = self.session.get_api()
        self.long_poll = VkLongPoll(self.session)

        self.keyboard = {
            "one_time": False,
            "buttons": [
                [get_button('Показать список маршрутов', 'positive')],
                [get_button('Помощь', 'negative')]
            ]
        }
        self.keyboard = json.dumps(self.keyboard, ensure_ascii=False).encode('utf-8')
        self.keyboard = str(self.keyboard.decode('utf-8'))

        self.tram_routes = get_routes()

    def send_message(self, user_id, message, keyboard):
        self.session.method('messages.send', {'user_id': user_id,
                                              'message': message,
                                              'random_id': 0,
                                              'keyboard': keyboard})

    def run(self):
        for event in self.long_poll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    user_id = event.user_id
                    message = event.text

                    if message.lower() == 'показать список маршрутов':
                        self.send_message(user_id, str_dict(self.tram_routes), self.keyboard)

                    elif message.lower() == 'помощь':
                        self.send_message(user_id,
                                          'Введите номер маршрута, чтобы увидеть расписание',
                                          self.keyboard)

                    elif message in self.tram_routes:
                        self.send_message(user_id,
                                          get_timetable(self.tram_routes[message]),
                                          self.keyboard)

                    else:
                        self.send_message(user_id,
                                          'Данный маршрут не найден',
                                          self.keyboard)
