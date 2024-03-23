import string
from datetime import datetime, UTC
import requests
import json
import aas


def Deleted() -> str:
    return '</deleted>'


class Struct:
    def __init__(self, dictionary: dict) -> None:
        for i in dictionary:
            if isinstance(dictionary[i], dict):
                dictionary[i] = Struct(dictionary[i])
            setattr(self, i, dictionary[i])

    def __str__(self) -> str:
        return getattr(self, '@')

    def json(self) -> str:
        r = {}
        for i in self.__dict__:
            if isinstance(self.__dict__[i], Struct):
                r.update({i: self.__dict__[i].json()})
            else:
                r.update({i: self.__dict__[i]})
        return json.dumps(r)


class User(Struct):
    def __init__(self, addr: str, fetch_as=None) -> None:
        self.__as = fetch_as
        self.__addr = addr
        r = requests.post(f"https://{aas.get(addr.split('@')[1])}/protocols/user_info", json={
            'username': addr.split('@')[0]
        })
        if r.status_code == 200:
            d = r.json()
            d['address'] = addr
            if 'social' not in d:
                d['social'] = False
            if fetch_as is None:
                d['relation'] = ''
                d['smtp'] = {}
                d['socials'] = {}
            else:
                r = fetch_as.request('list_contacts')
                if r.status_code == 200:
                    if addr in r.json():
                        c = r.json()[addr]
                        for i in c:
                            if isinstance(c[i], dict) or d[i.lowercase()].replace('*', '') == '':
                                d.update({i.lowercase(): c[i]})
            d['@'] = f"{d['name']} {d['surname']}"
            super().__init__(d)

    def save(self) -> bool:
        r = self.__as.request('edit_contact', json.dumps(self.json()))
        if r.status_code == 200:
            self.__init__(self.__addr, self.__as)
            return True
        else:
            return False

    def add_to_contacts(self, relation: str, smtp: dict, socials: dict) -> bool:
        if isinstance(smtp, dict) and isinstance(socials, dict) and isinstance(relation, str):
            r = self.__as.request('add_contact', relation='', smtp=smtp, socials=socials)
            if r.status_code == 200:
                self.__init__(self.__addr, self.__as)
                return True
            else:
                return False
        else:
            return False

    def delete_from_contacts(self) -> bool:
        r = self.__as.request('edit_contact', email=self.__addr, data=Deleted())
        if r.status_code == 200:
            self.__init__(self.__addr, self.__as)
            return True
        else:
            return False


class Network(Struct):
    def __init__(self, addr: str) -> None:
        r = requests.post(f"https://{aas.get(addr)}/protocols/version")
        if r.status_code == 200:
            d = r.json()
            d['@'] = addr
            super().__init__(d)

    def terms_of_service(self) -> str:
        r = requests.post(f"https://{aas.get(str(self))}/protocols/terms_of_service")
        if r.status_code == 200:
            return r.content.decode()

    def create_account(self,
                       username: str,
                       password: str,
                       name: str,
                       surname: str,
                       gender: str,
                       birthday: str,
                       country: str,
                       postcode: str,
                       timezone: int,
                       phone_number: int,
                       biography: str
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
            "username": username,
            "biography": biography
        }
        r = requests.post(f"https://{aas.get(str(self))}/protocols/signup", json=d)
        return r.status_code == 200


class Resource:
    def __init__(self, d: dict) -> None:
        self.title = d['title']
        self.url = d['url']
        self.description = d['description']

    def json(self) -> str:
        return json.dumps({
            'title': self.title,
            'url': self.url,
            'description': self.description
        })


class Post:
    def __init__(self, u, id: str) -> None:
        r = u.request('get_feed_post', id=id)
        if r.status_code == 200:
            d = r.json()
            self.title = d['title']
            self.datetime = datetime.strptime(d['datetime'], '%Y-%m-%d %H:%M')
            self.id = d['id']
            self.content = d['content']
        else:
            self.title = 'NotFound'
            self.datetime = datetime.now(UTC)
            self.id = id
            self.content = ''

    def json(self) -> str:
        return json.dumps({
            'title': self.title,
            'datetime': self.datetime.strftime('%Y-%m-%d %H:%M'),
            'id': self.id,
            'content': self.content
        })


class Contact:
    def __init__(self, d: dict) -> None:
        self.relation = d['Relation']
        self.smtp = Struct(d['SMTP'])
        self.socials = Struct(d['Socials'])
        self.id = Struct({})
        for i in d:
            if not hasattr(self, i):
                self.id.__dict__[i] = d[i]

    def json(self) -> str:
        r = json.loads(self.id.json())
        r.update({'Relation': self.relation})
        r.update({'SMTP': json.loads(self.smtp.json())})
        r.update({'Socials': json.loads(self.socials.json())})
        return json.dumps(r)


class SubReminder:
    def __init__(self, d: dict) -> None:
        self.deadline = datetime.strptime(d['deadline'], '%Y-%m-%d %H:%M')
        self.status = d['status']
        self.title = d['title']

    def json(self) -> str:
        return json.dumps({
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M'),
            'status': self.status,
            'title': self.title
        })


class Reminder:
    def __init__(self, d: dict) -> None:
        self.deadline = datetime.strptime(d['deadline'], '%Y-%m-%d %H:%M')
        self.last_update_status = datetime.strptime(d['last_update_status'], '%Y-%m-%d %H:%M')
        self.repeat = d['repeat']
        self.status = d['status']
        self.title = d['title']
        self.subs = []
        for i in d['subs']:
            self.subs.append(SubReminder(i))

    def json(self) -> str:
        r = {
            'deadline': self.deadline,
            'last_update_status': self.last_update_status,
            'repeat': str(self.repeat),
            'status': self.status,
            'title': self.title,
            'subs': []
        }
        for i in self.subs:
            r['subs'].append(json.loads(i.json()))
        return json.dumps(r)


class Message:
    def __init__(self, d: dict) -> None:
        self.sender = d['from']
        self.date_received = datetime.strptime(d['date_received'], '%Y-%m-%d %H:%M')
        self.body = d['body']

    def json(self) -> str:
        return json.dumps({
            'from': self.sender,
            'date_received': self.date_received.strftime('%Y-%m-%d %H:%M'),
            'body': self.body
        })


class Chat:
    def __init__(self, o, id: str, d: dict) -> None:
        self.__as = o
        self.last_index = d['last_index']
        if len([i for i in d]) == 1:
            idx = User(id)
            d = {'image': idx.profile_photo, 'title': id}
            self.participants = [User(str(o)), idx]
        else:
            self.participants = []
            for i in d['participants']:
                self.participants.append(User(i))
        self.image = d['image']
        self.title = d['title']
        self.id = id

    def get_message(self, index: int) -> (Message, None):
        r = self.__as.request('get_message', chat=self.id, id=index)
        if r.status_code == 200:
            return Message(r.json())
        else:
            return None

    def get_chat_history(self) -> list[Message]:
        r = self.__as.request('list_chats')
        if r.status_code == 200:
            self.__init__(self.__as, self.id, r.json()[self.id])
        d = []
        i = 0
        while i <= self.last_index:
            r = self.get_message(i)
            if r is not None:
                d.append(r)
            i += 1
        return d

    def send_message(self, body: str) -> bool:
        r = self.__as.request('send_message', chat=self.id, body=body)
        return r.status_code == 200

    def json(self) -> str:
        r = {
            'last_index': self.last_index,
            'image': self.image,
            'participants': [],
            'title': self.title
        }
        for i in self.participants:
            # noinspection PyUnresolvedReferences
            r['participants'].append(i.address)
        return json.dumps(r)


class Mail:
    def __init__(self, user, mailbox: str, index: int) -> None:
        self.__as = user
        self.__mailbox = mailbox
        self.__index = index
        r = user.request('get_mail', mailbox=mailbox, id=index)
        if r.status_code == 200:
            d = r.json()
            self.subject = d['subject']
            self.sender = d['sender']
            self.date_received = datetime.strptime(d['date_received'], '%Y-%m-%d %H:%M')
            self.body = d['body']
            self.to = d['to']
            self.cc = d['cc']
            self.hashtag = (d['hashtag'] if d['hashtag'] != '' else None)
        else:
            self.subject = None
            self.sender = None
            self.date_received = datetime.now(UTC)
            self.body = None
            self.to = None
            self.cc = None
            self.hashtag = None

    def __str__(self) -> str:
        return f'''
Subject: {self.subject}
From: {self.sender}
To: {', '.join(self.to)}
CC: {', '.join(self.cc)}
Received: {self.date_received.strftime('%Y-%m-%d %H:%M')}
Hashtag: {self.hashtag}

{self.body}

        '''

    def __bool__(self) -> bool:
        return self.subject is not None

    def move(self, to: str) -> bool:
        r = self.__as.request('move_mail', mailbox=self.__mailbox, id=self.__index, move_to=to)
        if r.status_code == 200:
            self.subject = None
            self.sender = None
            self.date_received = datetime.now(UTC)
            self.body = None
            self.to = None
            self.cc = None
            self.hashtag = None
            return True
        else:
            return False

    def delete(self) -> bool:
        return self.move('-')

    def json(self) -> str:
        return json.dumps({
            "subject": self.subject,
            "date_received": self.date_received.strftime('%Y-%m-%d %H:%M'),
            "sender": self.sender,
            "to": self.to,
            "cc": self.cc,
            "hashtag": self.hashtag,
            "body": self.body
        })
