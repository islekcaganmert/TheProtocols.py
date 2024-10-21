import requests
from TheProtocols.objects.network import OS, Software
from typing import Any


class Token:
    def __init__(self, session, domain: str) -> None:
        self.__session = session
        self.__domain = domain  # domain of proxy between TheProtocols and blockchain
        resp = requests.get(f'https://{self.__domain}/protocols/token/about')
        if resp.status_code == 200:
            self.exchange = resp.json()['exchange']
            self.name = resp.json()['name']
            self.network = resp.json()['network']
            self.os = OS(**resp.json()['os'])
            self.software = Software(**resp.json()['software'])
            self.version = resp.json()['version']
        else:
            self.exchange = None
            self.name = None
            self.network = None
            self.os = None
            self.software = None
            self.version = None

    def init_subclass(self, subclass) -> Any:
        return type(subclass.__name__, (Token, ), {
            '__session': self.__session,
            '__domain': self.__domain,
            'exchange': self.exchange,
            'name': self.name,
            'network': self.network,
            'os': self.os,
            'software': self.software,
            'version': self.version,
            'get_session': subclass.get_session,
            'get_public_address': subclass.get_public_address,
            'sign': subclass.sign,
            'balance': self.balance,
            'transfer': subclass.transfer if subclass.overwrite_transfer else self.transfer
        })

    def get_session(self) -> Any:
        return self.__session

    def get_public_address(self) -> str:
        raise NotImplementedError("This method must be implemented by the subclass.")

    def sign(self, d) -> str:
        raise NotImplementedError("This method must be implemented by the subclass.")

    @property
    def balance(self) -> int:
        addr = self.get_public_address()
        resp = requests.post(f'https://{self.__domain}/protocols/token/balance', json={'address': addr})
        if resp.status_code == 200:
            return int(resp.content.decode())
        else:
            return 0

    def transfer(self, to: str = None, amount: int = None, transactions: list[dict] = None) -> bool:
        dt = {
            'address': self.get_public_address(),
            'signature': None,
            'transactions': []
        }
        if transactions is not None:
            for i in transactions:
                if 'to' not in i or 'amount' not in i:
                    raise AttributeError("All transactions must have a 'to' and 'amount' key.")
                dt['transactions'].append({'from': dt['address'], 'to': i['to'], 'amount': i['amount']})
        elif not isinstance(to, str) and not isinstance(amount, int):
            dt['transactions'].append({'from': dt['address'], 'to': to, 'amount': amount})
        else:
            raise AttributeError("'transactions' or either 'to' and 'amount' must be provided.")
        dt['signature'] = self.sign(dt)
        return requests.post(
            f'https://{self.__domain}/protocols/token/transfer',
            json=dt
        ).status_code == 200
