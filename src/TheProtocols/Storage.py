from typing import Any

from .ID import ID
from .Objects import Struct


class Storage:
    def __init__(self, id: ID) -> None:
        self.id = id

    def __getattr__(self, item: str) -> Any:
        if item == 'status':
            r = self.id.request('storage_status')
            if r.status_code == 200:
                if [i for i in r.json()] == ['total', 'used']:
                    used = {}
                    d = r.json()
                    for i in d['used']:
                        used.update({i: int(d['used'][i])})
                    return Struct({'total': int(r.json()['total']), 'used': used})
            else:
                return Struct({'total': 0, 'used': {}})
