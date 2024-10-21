from datetime import datetime, UTC


class Message:
    def __init__(self, s, chat, index) -> None:
        self.__session = s
        self.__chat = chat
        self.__index = index
        resp = self.__session.request('get_message', chat=self.__chat, id=self.__index)
        if resp.status_code == 200:
            self.sender = resp.json()['from']
            self.body = resp.json()['body']
            self.date_received = resp.json()['date_received']
        else:
            self.sender = ''
            self.body = ''
            self.date_received = datetime.now(UTC).strftime('%Y-%m-%d %H:%M')


class Chat:
    def __init__(self, session, id: str):
        self.__session = session
        self.__id = id
        self.last_index = 0
        self.image = ''
        self.title = ''
        self.participants = []

    def get_message(self, index) -> Message:
        return Message(self.__session, self.__id, index)

    def send_message(self, message) -> bool:
        r = self.__session.request('send_message', chat=self.__id, body=message)
        return r.status_code == 200
