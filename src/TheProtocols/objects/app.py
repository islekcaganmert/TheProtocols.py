import requests


class App:
    def __init__(self, package_name, secure: bool = True, data: dict = None, s=None) -> None:
        self.package_name = package_name
        self.secure = secure
        self.__fetch_cache = None
        self.__s = s
        if data is not None:
            for i in data:
                setattr(self, i, data[i])

    name = property(lambda self: self.fetch()['name'])
    icon = property(lambda self: self.fetch()['icon'])
    description = property(lambda self: self.fetch()['description'])
    latest_version = property(lambda self: self.fetch()['latest_version'])
    latest_build_number = property(lambda self: self.fetch()['latest_build_number'])
    default_preferences = property(lambda self: self.fetch()['preferences'])
    developer = property(lambda self: self.fetch()['developer'])

    def fetch(self) -> dict:
        if self.__fetch_cache is None:
            pieces = self.package_name.split('.')
            pieces.reverse()
            domain = '.'.join(pieces)
            resp = requests.get(f"http{'s' if self.secure else ''}://{domain}/.well-known/app_info.json")
            if resp.status_code == 200:
                self.__fetch_cache = resp.json()
            else:
                self.__fetch_cache = {
                    "name": "",
                    "icon": "",
                    "description": "",
                    "latest_version": "",
                    "latest_build_number": 0,
                    "developer": "",
                    "preferences": {}
                }
        return self.__fetch_cache

    def data(self, d: dict = None) -> dict:
        if d is not None:
            self.__s.request('push_library_data', app=self.package_name, data=d)
        resp = self.__s.request('pull_library_data', app=self.package_name)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {}

    def preferences(self, d: dict = None) -> dict:
        if d is not None:
            self.__s.request('push_app_preferences', app=self.package_name, data=d)
        resp = self.__s.request('pull_app_preferences', app=self.package_name)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {}
