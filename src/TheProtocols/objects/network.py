import json
import string
from datetime import datetime
import requests
from TheProtocols.helpers.exceptions import NetworkException


class MembershipPlan:
    def __init__(self, name: str, storage) -> None:
        self.name = name
        self.storage = storage


class OS:
    def __init__(self, family: str, name: str, version: str, arch: str) -> None:
        self.family = family
        self.name = name
        self.version = version
        self.arch = arch


class Rules:
    def __init__(self, new_accounts_allowed: bool) -> None:
        self.new_accounts_allowed = new_accounts_allowed


class Software:
    def __init__(self, build: str, channel: str, developer: str, name: str, source: str, version: str) -> None:
        self.build = build
        self.channel = channel
        self.developer = developer
        self.name = name
        self.source = source
        self.version = version

    def json(self) -> str:
        return json.dumps({
            "build": self.build,
            "channel": self.channel,
            "developer": self.developer,
            "name": self.name,
            "source": self.source,
            "version": self.version
        })


class Network:
    def __init__(self, addr: str, secure: bool = True) -> None:
        self.addr = addr
        self.secure = secure
        r = requests.get(f"http{'s' if secure else ''}://{str(self)}/protocols/version")
        if r.status_code == 200:
            d = r.json()
            self.version = float(d['version'])
            if self.version >= 3.0:
                self.help = d['help']
                self.os = OS(**{
                    'family': d['os']['family'],
                    'name': d['os']['name'],
                    'version': d['os']['version'],
                    'arch': d['os']['arch']
                })
                self.rules = Rules(**{
                    "new_accounts_allowed": d['rules']['new_accounts_allowed']
                })
                self.software = Software(**{
                    "build": d['software']['build'],
                    "channel": d['software']['channel'],
                    "developer": d['software']['developer'],
                    "name": d['software']['name'],
                    "source": d['software']['source'],
                    "version": d['software']['version']
                })
                self.users = []
                for i in d['users']:
                    self.users.append(i)
            if self.version >= 3.1:
                self.membership_plans = []
                if self.version >= 3.1:
                    for i in d['membership_plans']:
                        self.membership_plans.append(MembershipPlan(i['name'], i['storage']))
                else:
                    self.membership_plans.append(MembershipPlan("Free", 0))
            else:
                self.membership_plans = [
                    MembershipPlan("Free", 0),
                    MembershipPlan("Plus", 0),
                    MembershipPlan("Plus", 0),
                    MembershipPlan("Plus", 0)
                ]
        else:
            raise NetworkException(f"Network is not available: {r.status_code}")

    def __str__(self) -> str:
        return self.addr

    __repr__ = __str__

    def protocol(self, endpoint: str) -> str:
        if self.secure:
            return f"https://{str(self)}/protocols/{endpoint}"
        else:
            # noinspection HttpUrlsUsage
            return f"http://{str(self)}/protocols/{endpoint}"

    def terms_of_service(self) -> str:
        r = requests.post(self.protocol("terms_of_service"))
        if r.status_code == 200:
            return r.content.decode()

    def create_account(
        self,
        username: str,
        password: str,
        name: str,
        surname: str,
        gender: str,
        birthday: str,
        country: str,
        postcode: str,
        timezone: int,
        phone_number: str
    ) -> bool:
        t = username
        for i in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-':
            t = t.replace(i, '')
        if t != '':
            raise ValueError('Invalid username')
        t = country
        for i in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            t = t.replace(i, '')
        if t != '' or len(country) != 2:
            raise ValueError('Invalid country code')
        try:
            datetime.strptime(birthday, '%Y-%m-%d')
        except Exception as e:
            raise ValueError(f"Invalid birthday: {str(e)}")
        if gender not in [
            'Male',
            'Female',
            'Lesbian',
            'Gay',
            'Bisexual',
            'Transgender',
            'Queer',
            'Intersexual',
            'Asexual',
            'Pansexual'
        ]:
            raise ValueError('Invalid gender')
        d = {
            "birthday": birthday,
            "country": country,
            "gender": gender,
            "name": string.capwords(name),
            "password": password,
            "phone_number": str(phone_number),
            "postcode": postcode,
            "timezone": timezone,
            "surname": surname.upper(),
            "username": username
        }
        if 3.0 <= self.version < 3.1:
            d['biography'] = ""
        r = requests.post(self.protocol('signup'), json=d)
        return r.status_code == 200
