import json

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

from TheProtocols.helpers.exceptions import CredentialsDidntWorked, NetworkException
from TheProtocols.objects.mail import Mailbox
from TheProtocols.objects.network import Network
from TheProtocols.objects.user import User as UserObject
from TheProtocols.objects.app import App
from TheProtocols.objects.resource import Resource
from TheProtocols.objects.chat import Chat


class DynamicObject:
    def __init__(self, d: dict) -> None:
        self.__dict__['_attributes'] = {}
        for i in d:
            self.__dict__['_attributes'][i] = d[i]

    def __getattr__(self, name) -> any:
        if name in self._attributes:
            if isinstance(self._attributes[name], dict):
                return DynamicObject(self._attributes[name])
            return self._attributes[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value) -> None:
        self._attributes[name] = value

    def __delattr__(self, name) -> None:
        if name in self._attributes:
            del self._attributes[name]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._attributes})"


class Post:
    def __init__(self, s, id) -> None:
        self.id = id
        resp = s.request('get_feed_post', id=id)
        if resp.status_code == 200:
            self.title = resp.json()['title']
            self.content = resp.json()['content']
            self.datetime = resp.json()['datetime']
        else:
            self.title = None
            self.content = None
            self.datetime = None


class User:
    def __init__(self, s) -> None:
        self.__email = lambda: str(s)
        self.network = s.network
        r = s.request('current_user_info')
        if r.status_code == 200:
            d = r.json()
            self.name = d['name']
            self.surname = d['surname']
            self.country = d['country']
            self.birthday = d['birthday']
            self.rsa_public_key = d['rsa_public_key']
            self.gender = d['gender']
            self.phone_number = d['phone_number']
            self.plus = d['plus']
            self.timezone = d['timezone']
            self.postcode = d['postcode']
            self.profile_photo = d['profile_photo']
            self.relation = 'Self'
            self.socials = []
            self.rsa_private_key = d['rsa_private_key']
            self.settings = DynamicObject(d['settings'])
    json = UserObject.json
    __str__ = __repr__ = UserObject.__str__
    verify = UserObject.verify


class Session:
    def __init__(self, app, email, password, token=None) -> None:
        self.__email = email
        self.__password = password
        self.__app = app
        self.network = Network(email.split('@')[1], secure=app.secure)
        if isinstance(password, str) and token is None:
            if 3.0 <= self.network.version < 3.1:
                self.id = User(self)
                self.token = None
            else:
                r = requests.post(self.network.protocol('login'), json={
                    'username': email.split('@')[0],
                    'password': password,
                    'package': app.package_name,
                    'permissions': app.permissions
                })
                if r.status_code == 200:
                    self.token = r.json()['token']
                    self.id = User(self)
                else:
                    raise CredentialsDidntWorked
        elif isinstance(token, str):
            self.token = token
            self.id = User(self)
        else:
            raise AttributeError('Password or Token must be provided')

    def request(self, endpoint, **kwargs) -> requests.Response:
        data = {i: kwargs[i] for i in kwargs}
        if 3.0 <= self.network.version < 3.1:
            data.update({'current_user_username': str(self).split('@')[0], 'current_user_password': self.__password})
        else:
            data.update({'cred': self.token})
        return requests.post(self.network.protocol(endpoint), json=data)

    def sign(self, data: str) -> str:
        return serialization.load_pem_private_key(
            self.id.rsa_private_key.encode(),
            password=None,
            backend=default_backend()
        ).sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA512()
        ).hex()

    def data(self, d: dict = None) -> dict:
        if d is not None:
            self.request('push_library_data', app=self.__app.package_name, data=d)
        resp = self.request('pull_library_data', app=self.__app.package_name)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {}

    def preferences(self, d: dict = None) -> dict:
        if d is not None:
            self.request('push_app_preferences', app=self.__app.package_name, data=d)
        resp = self.request('pull_app_preferences', app=self.__app.package_name)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {}

    def interapp(self, package_name: str):
        return App(package_name, self.__app.secure, s=self)

    def modify_id(self, key: str, value) -> bool:
        r = self.request('set_user_data', key=key, value=value)
        if r.status_code == 200:
            self.__init__(self.__app, self.__email, self.__password)
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
                s = self.__app.get_cached(Post, 'id', i['id'], s=self)
                d.append(s)
            return d
        else:
            return []

    def get_mailboxes(self) -> list[Mailbox]:
        r = self.request('list_mailboxes')
        if r.status_code == 200:
            d = r.json()
            return [Mailbox(self, i, d[i]) for i in d]
        else:
            return []

    def send_mail(
            self,
            to: str,
            cc: str = '',
            bcc: str = '',
            subject: str = 'No Subject',
            body: str = '',
            hashtag: str = ''
    ) -> bool:
        r = self.request('send_mail', subject=subject, body=body, to=to, cc=cc, bcc=bcc, hashtag=hashtag)
        if r.status_code == 200:
            return True
        else:
            return False

    def list_chats(self) -> dict[str, (Chat, type)]:
        r = self.request('list_chats')
        if r.status_code == 200:
            d: dict = r.json()['chats']
            return {str(i): type('Chat', (), {
                "last_index": d[i]['last_index'],
                "image": d[i]['image'],
                "title": d[i]['title'],
                "participants": d[i]['participants'],
                "__id": i,
                "__session": self,
                "__init__": Chat.__init__,
                "get_message": Chat.get_message,
                "send_message": Chat.send_message
            }) for i in d}
        else:
            return {}

    def create_chat(self, title: str, image: str, participants: list[str]) -> bool:
        return self.request('send_message', chat="/", body=json.dumps({
            "image": image,
            "title": title,
            "participants": participants
        })).status_code == 200

    def list_contacts(self) -> list[User]:
        r = self.request('list_contacts')
        if r.status_code == 200:
            d = []
            for i in r.json():
                try:
                    d.append(UserObject(i, self, self.__app.secure))
                except NetworkException:
                    pass
            return d
        else:
            return []

    def __str__(self) -> str:
        return self.__email

    __repr__ = __str__
