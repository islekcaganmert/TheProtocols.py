from datetime import datetime
import requests
from TheProtocols.session import Session


class File:
    def __init__(self, d: dict, session: Session, path: str) -> None:
        self.type: str = d['type']
        self.size: int = d['size']
        self.created: datetime = datetime.strptime(d['created'], '%Y-%m-%d %H:%M')
        self.edited: datetime = datetime.strptime(d['edited'], '%Y-%m-%d %H:%M')
        self._session = session
        self._path = path.replace('//', '/')

    def _request(self, method: str, body: (str, bytes) = None) -> requests.Response:
        if not self._session:
            raise Exception('No session provided')
        return getattr(requests, method.lower())(
            (
                f"http{'s' if self._session.network.secure else ''}://{self._session.network}/protocols/storage/" +
                f"{str(self._session).split('@')[0]}{self._path}"
            ).replace('//', '/').replace(':/', '://'),
            headers={'Authorization': f"TheProtocols-Token {self._session.token}"},
            **({'data': body} if method.upper() == 'POST' else {})
        )

    def read(self) -> (str, bytes, None):
        r = self._request('GET')
        if r.status_code != 200:
            return None
        try:
            return r.content.decode()
        except UnicodeDecodeError:
            return r.content

    def write(self, data: (str, bytes)) -> bool:
        r = self._request('POST', data)
        return r.status_code == 200


class UsedStorage:
    def __init__(self, d: dict) -> None:
        self.id = int(d.get('id', 0))
        self.apps = int(d.get('apps', 0))
        self.mails = int(d.get('mails', 0))
        self.notes = int(d.get('notes', 0))
        self.reminders = int(d.get('reminders', 0))
        self.tokens = int(d.get('tokens', 0))
        for i in d:
            if i not in ['id', 'apps', 'mails', 'notes', 'reminders', 'tokens']:
                setattr(self, i, int(d[i]))


class StorageStatus:
    def __init__(self, d: dict) -> None:
        self.total = int(d['total'])
        self.used = UsedStorage(d['used'])


class Storage:
    def __init__(self, id) -> None:
        self.id = id
        self.cwd = '/'

    @property
    def status(self) -> StorageStatus:
        r = self.id.request('storage_status')
        d = None
        if r.status_code == 200:
            if [i for i in r.json()] == ['total', 'used']:
                d = r.json()
        if d is None:
            d = {'total': 0, 'used': {}}
        return StorageStatus(d)

    def _get_full_path(self, path: str) -> str:
        if not path.startswith('/'):
            path = f"{self.cwd}{path}"
        pieces = path.split('/')
        while '..' in pieces:
            i = pieces.index('..')
            if pieces[i] == '..':
                pieces.pop(i)
                pieces.pop(i - 1)
        return '/' + '/'.join(pieces)

    def listdir(self, path: str = None) -> (dict[str, File], None):
        if path is None:
            path = self.cwd
        path = self._get_full_path(path)
        r = self.id.request('storage_ls', path=path)
        if r.status_code != 200:
            return None
        d = r.json()
        return {str(i): File(d[i], self.id, f"{path}/{i}") for i in d}

    def chdir(self, path: str) -> bool:
        path = self._get_full_path(path)
        if self.listdir(path) is not None:
            self.cwd = path
            return True

    def mkdir(self, path: str) -> bool:
        path = self._get_full_path(path)
        r = self.id.request('storage_new_folder', folder=path)
        return r.status_code == 200

    def remove(self, path: str) -> bool:
        path = self._get_full_path(path)
        r = self.id.request('storage_delete', path=path)
        return r.status_code == 200

    def open(self, path: str) -> (str, None):
        path = self._get_full_path(path).removesuffix('/')
        r = self.listdir(path)
        if r is None:
            raise FileNotFoundError
        try:
            return File(r[path.split('/')[-1]], self.id, path)
        except KeyError:
            return None

    def new_file(self, path: str) -> (str, None):
        path = self._get_full_path(path).removesuffix('/')
        p = path.removesuffix(f"/{path.split('/')[-1]}")
        r = self.listdir(p)
        if r is None:
            raise FileNotFoundError
        try:
            return File({
                'type': 'text/plain',
                'size': 0,
                'created': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'edited': datetime.now().strftime('%Y-%m-%d %H:%M')
            }, self.id, path)
        except KeyError:
            return None
