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

    def __getattr__(self, item: str) -> StorageStatus:
        if item == 'status':
            r = self.id.request('storage_status')
            d = None
            if r.status_code == 200:
                if [i for i in r.json()] == ['total', 'used']:
                    d = r.json()
            if d is None:
                d = {'total': 0, 'used': {}}
            return StorageStatus(d)
