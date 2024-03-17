import json


class DataRoot:
    def __init__(self, id, root: str):
        self.__root = root
        self.__id = id

    def __iter__(self):
        r = []
        for i in self.__id.id.settings.apps:
            if i.removeprefix(f'{self.__root}.').split('.')[0] not in r:
                r.append(i.removeprefix(f'{self.__root}.').split('.')[0])
        if '' in r:
            r.remove('')
            r.append('.')
        return r

    def __getattr__(self, item):
        return DataRoot(self.__id, f'{self.__root}.{item}'.removeprefix('.'))

    def get_root(self):
        return self.__root

    def __call__(self, data: dict = None):
        if data is not None:
            self.__id.request('push_library_data', app=self.__root, data=json.dumps(data))
        r = self.__id.request('pull_library_data', app=self.__root)
        if r.status_code == 200:
            return r.json()
        else:
            return {}
