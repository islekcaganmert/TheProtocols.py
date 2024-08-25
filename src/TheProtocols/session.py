import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from TheProtocols.objects.network import Network
from TheProtocols.objects.user import User as UserObject
from TheProtocols.objects.app import App
from TheProtocols.objects.resource import Resource


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
    json = UserObject.json
    __str__ = __repr__ = UserObject.__str__
    verify = UserObject.verify


class Session:
    def __init__(self, app, email, password) -> None:
        self.__email = email
        self.__password = password
        self.__app = app
        self.network = Network(email.split('@')[1], secure=app.secure)
        if 3.0 <= self.network.version < 3.1:
            self.id = User(self)
            self.token = None
        else:
            r = requests.post(self.network.protocol('login'), json={
                'username': email.split('@')[0],
                'password': password,
                'package': app.package_name,
                'signature': app.application_token,
                'permissions': app.permissions
            })
            if r.status_code == 200:
                self.token = r.json()['token']
                self.id = User(self)
            else:
                self.token = None

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

    #    To Do List
    # 1. Chats
    # 2. Mail
    # 3. Feed
    # 4. Notes
    # 5. Reminders
    # 6. Storage
    # 7. Token

    def __str__(self) -> str:
        return self.__email

    __repr__ = __str__