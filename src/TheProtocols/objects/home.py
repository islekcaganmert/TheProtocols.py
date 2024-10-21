from TheProtocols import *


class Thing:
    def __init__(self, s, name: str):
        self._s = s
        self._name = name

    def __str__(self) -> str:
        return self._name
    __repr__ = __str__

    @property
    def status(self) -> (dict, None):
        resp = self._s.request('get_thing', thing=self._name)
        if resp.status_code == 200:
            return resp.json()
        else:
            return None

    def set_status(self, **kwargs) -> bool:
        resp = self._s.request('set_thing', thing=self._name, modified=kwargs)
        return resp.status_code == 200


class Room:
    def __init__(self, owner, s, name: str):
        self._o = owner
        self._s: Session = s
        self._name = name

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"'{self._name}'"

    def unregister_thing(self, name: str) -> bool:
        return self._o.unregister_thing(name)

    def register_thing(self, name: str, url: str) -> bool:
        resp = self._s.request('register_thing', name=name, room=self._name, url=url)
        return resp.status_code == 200

    @property
    def things(self) -> list[Thing]:
        resp = self._s.request('list_things', room=self._name)
        if resp.status_code == 200:
            return resp.json()
        else:
            return []


class Home:
    def __init__(self, s) -> None:
        self._s = s

    def create_room(self, name: str) -> bool:
        resp = self._s.request('create_room', name=name)
        return resp.status_code == 200

    def delete_room(self, name: str) -> bool:
        resp = self._s.request('delete_room', name=name)
        return resp.status_code == 200

    def unregister_thing(self, name: str) -> bool:
        resp = self._s.request('unregister_thing', thing=name)
        return resp.status_code == 200

    @property
    def rooms(self) -> list[Room]:
        resp = self._s.request('list_rooms')
        if resp.status_code == 200:
            return [Room(self, self._s, i) for i in resp.json()]
        else:
            return []
