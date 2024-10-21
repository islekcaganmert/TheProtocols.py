import hashlib
import os.path
import subprocess


class Album:
    def __init__(self, s, name: str):
        self._s = s
        self._name = name

    def add_photo(self, name: str) -> bool:
        return self._s.request('add_photo_album', album=self._name, name=name).status_code == 200

    def remove_photo(self, name: str) -> bool:
        return self._s.request('remove_photo_album', album=self._name, name=name).status_code == 200

    @property
    def photos(self) -> list[str]:
        resp = self._s.request('list_photos_album', album=self._name)
        if resp.status_code == 200:
            return resp.json()
        else:
            return []


class Photos:
    def __init__(self, s) -> None:
        self._s = s

    def get_album(self, name: str) -> Album:
        return Album(self._s, name)

    def create_album(self, name: str) -> bool:
        resp = self._s.request('create_album', name=name)
        return resp.status_code == 200

    def delete_album(self, name: str) -> bool:
        resp = self._s.request('delete_album', name=name)
        return resp.status_code == 200

    def bulk_day(self, day: str) -> dict:
        resp = self._s.request('list_photos', date=day)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {
                'list': [],
                'previous': None,
                'next': None
            }

    def day(self, day: str) -> list[str]:
        return self.bulk_day(day)['list']

    def get(self, name: str) -> tuple[bytes, dict[str, str]]:
        resp = self._s.request('get_photo', filename=name)
        if resp.status_code == 200:
            d = resp.json()
            content = bytes.fromhex(d['hex'])
            if hashlib.sha512(content).hexdigest() == d['hash']:
                return content, {
                    "filetype": d['filetype'],
                    "albums": d['albums'],
                    "date": d['date']
                }
        else:
            return b'', {
                "filetype": 'empty',
                "albums": [],
                "date": ''
            }

    def save(self, path: str) -> bool:
        if not os.path.exists(path):
            return False
        content = open(path, 'rb').read()
        return self._s.request(
            'save_photo',
            hex=content.hex(),
            hash=hashlib.sha512(content).hexdigest(),
            filetype=subprocess.run(['file', '-b', path], capture_output=True).stdout.decode().strip('\n'),
        ).status_code == 200

    def delete(self, name: str) -> bool:
        return self._s.request('delete_photo', filename=name).status_code == 200

    def move_to_trash(self, name: str) -> bool:
        return self._s.request('move_photo_trash', filename=name).status_code == 200

    @property
    def trash(self) -> list[str]:
        resp = self._s.request('list_photos_trash')
        if resp.status_code == 200:
            return resp.json()
        else:
            return []

    @property
    def albums(self) -> list[str]:
        resp = self._s.request('list_albums')
        if resp.status_code == 200:
            return resp.json()
        else:
            return []
