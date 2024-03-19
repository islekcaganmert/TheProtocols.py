from .Helpers.Exceptions import TokenException
from .Objects import Struct, User
from .ID import ID
import requests
import aas
import os

with open(f"{os.path.dirname(os.path.abspath(__file__))}/Version.py", 'r') as f:
    v = f.read()


class Token:
    def __init__(self, id: ID, address: str) -> None:
        self.__addr = address
        self.__id = id
        r = requests.post(f"https://{aas.get(address)}/protocols/token/about")
        if r.status_code == 200:
            d = r.json()
            if d['version'] == v:
                self.__exchange = d['exchange']
                self.name = d['name']
                self.os = Struct(d['os'])
                self.software = Struct(d['software'])
            else:
                if float(d['version']) > float(v):
                    old = 'SDK'
                else:
                    old = 'Token'
                raise TokenException(f'{old} is out-dated')
        else:
            raise TokenException('Token is not compatible')

    def get_exchange_rate(self) -> int:
        r = requests.post(f"https://{aas.get(self.__addr)}/protocols/token/about")
        if r.status_code == 200:
            d = r.json()
            if d['version'] == v:
                self.__exchange = d['exchange']
        return float(self.__exchange)

    def get_balance(self, user=None) -> int:
        if user is None:
            user = self.__id.id
        r = requests.post(f"https://{aas.get(self.__addr)}/protocols/token/balance", json={
            'public_key': user.chamychain_public_key
        })
        if r.status_code == 200:
            try:
                return int(r.content.decode())
            except ValueError:
                return 0
        else:
            return 0

    def transfer(self, receiver: User, amount: int) -> bool:
        r = requests.post(f"https://{aas.get(self.__addr)}/protocols/token/balance", json={
            'private_key': self.__id.id.chamychain_private_key,
            'receiver': receiver.chamychain_public_key,
            'amount': amount
        })
        return r.status_code == 200

    def __str__(self) -> str:
        return self.name
