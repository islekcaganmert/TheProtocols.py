from typing import Any

from .Helpers.Exceptions import NetworkException, CredentialsDidntWorked
from .Objects import Struct, Network, Resource, Post, Chat
from .Helpers.Cache import get_cached_object, add_to_cache
from .Data import DataRoot
from .Mailbox import Mailbox
import requests
import os
import aas
import json

with open(f"{os.path.dirname(os.path.abspath(__file__))}/Version.py", 'r') as f:
    v = f.read()


class ID:
    __network: str = "hereus.net"
    __username: str = "Guest"
    __password: str = ""
    id: Struct = Struct({})
    network: Struct = Struct({})

    def __init__(self, email: str, password: str) -> None:
        self.network = Network(email.split('@')[1])
        if self.network.version != v:
            if float(self.network.version) > float(v):
                old = 'SDK'
            else:
                old = 'Network'
            raise NetworkException(f"{old} is out-dated")
        r = requests.post(f"https://{aas.get(email.split('@')[1])}/protocols/current_user_info", json={
            'current_user_username': email.split('@')[0],
            'current_user_password': password
        })
        if r.status_code != 200:
            raise CredentialsDidntWorked()
        self.id = Struct(r.json())
        self.id.__dict__['@'] = f"{self.id.name} {self.id.surname}"
        if not hasattr(self.id, 'settings'):
            raise CredentialsDidntWorked()
        self.__username, self.__network = email.split('@')
        self.__password = password

    def __str__(self) -> str:
        return f"{self.__username}@{self.__network}"

    def request(self, endpoint: str, **data) -> requests.Response:
        d = {'current_user_username': self.__username, 'current_user_password': self.__password}
        for i in data:
            d.update({i: data[i]})
        r = requests.post(f"https://{aas.get(self.__network)}/protocols/{endpoint}", json=d)
        return r

    def modify_id(self, key: str, value: Any) -> bool:
        r = self.request('set_user_data', key=key, value=value)
        if r.status_code == 200:
            self.__init__(f"{self.__username}@{self.__network}", self.__password)
            return True
        else:
            return False

    def search(self, key: str) -> list[Resource]:
        r = self.request('search', key=key)
        if r.status_code == 200:
            d = []
            for i in r.json()['results']:
                d.append(Resource(i))
            return d
        else:
            return []

    def feed(self) -> list[Post]:
        r = self.request('get_feed')
        if r.status_code == 200:
            d = []
            for i in r.json()['feed']:
                s = get_cached_object(Post, 'id', i['id'])
                if not s:
                    s = Post(self, i['id'])
                    add_to_cache(s)
                d.append(s)
            return d
        else:
            return []

    def chats(self) -> list[Chat]:
        r = self.request('list_chats')
        if r.status_code == 200:
            d = []
            j = r.json()
            for i in j:
                d.append(Chat(self, i, j[i]))
            return d
        else:
            return []

    def create_chat(self, id: str, title: str, image: str, participants: list[str]) -> bool:
        r = self.request('send_message', chat='/', body=json.dumps({
            'title': title,
            'image': image,
            'participants': participants,
            'id': id
        }))
        return r.status_code == 200

    def list_mailboxes(self) -> dict[str, Mailbox]:
        r = self.request('list_mailboxes')
        d = {}
        for i in ['Primary', 'Promotions', 'Social', 'Spam', 'Sent', 'Archive', 'Trash']:
            d.update({i: Mailbox(self, i, 0)})
        if r.status_code == 200:
            g = r.json()
            for i in g:
                d.update({i: Mailbox(self, i, g[i])})
        return d

    def send_mail(self, to: list, cc: list, bcc: list, subject: str, body: str, hashtag: str) -> bool:
        r = self.request('send_mail',
                         to=';'.join(to), cc=';'.join(cc), bcc=';'.join(bcc),
                         subject=subject, body=body, hashtag=hashtag)
        return r.status_code == 200

    def __getattr__(self, item) -> (DataRoot, None):
        if item == 'data':
            return DataRoot(self, '')
        else:
            return None
