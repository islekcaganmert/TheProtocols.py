from datetime import datetime
from TheProtocols.objects.deleted import Deleted


class Location:
    def __init__(self, data) -> None:
        self.name = data['name']
        self.street = data['street']
        self.no = data['no']
        self.zipcode = data['zipcode']
        self.country = data['country']


class Event:
    def __init__(self, s, id, data) -> None:
        self.__session = s
        self.id = id
        self.name = data['name']
        self.starts = datetime.strptime(data['starts'], '%Y-%m-%d %H:%M')
        self.ends = datetime.strptime(data['ends'], '%Y-%m-%d %H:%M')
        self.location = Location(data['location'])
        self.alerts = data['alerts']
        self.repeat = data['repeat']
        self.travel_time = data['travel_time']
        self.participants = data['participants']
        self.notes = data['notes']
        self.url = data['url']
        self.attachments = data['attachments']

    def __str__(self) -> str:
        return self.name
    __repr__ = __str__

    def save(self) -> bool:
        return self.__session.request(
            'edit_event',
            id=self.id,
            object={
                'name': self.name,
                'starts': self.starts.strftime('%Y-%m-%d %H:%M'),
                'ends': self.ends.strftime('%Y-%m-%d %H:%M'),
                'location': {
                    'name': self.location.name,
                    'street': self.location.street,
                    'no': self.location.no,
                    'zipcode': self.location.zipcode,
                    'country': self.location.country
                },
                'alerts': self.alerts,
                'repeat': self.repeat,
                'travel_time': self.travel_time,
                'participants': self.participants,
                'notes': self.notes,
                'url': self.url,
                'attachments': self.attachments
            }
        ).status_code == 200

    def delete(self) -> None:
        if self.__session.request(
            'edit_event',
            id=self.id,
            object=Deleted
        ).status_code == 200:
            self.id = None
            self.name = None
            self.starts = None
            self.ends = None
            self.location = None
            self.alerts = None
            self.repeat = None
            self.travel_time = None
            self.participants = None
            self.notes = None
            self.url = None
            self.attachments = None


class Calendar:
    def __init__(self, s) -> None:
        self.__session = s
        self.__cal: list[Event] = []
        self.__start = self.__end = None

    def sync(self) -> None:
        resp = self.__session.request(
            'list_events',
            start=self.__start.strftime('%Y-%m-%d %H:%M'),
            end=self.__end.strftime('%Y-%m-%d %H:%M')
        )
        if resp.status_code == 200:
            self.__cal = []
            with resp.json() as data:
                for i in data:
                    self.__cal.append(Event(self.__session, i, data[i]))

    def fetch_until(self, year: int, month: int = None, day: int = None, hour: int = None):
        if self.__start is not None and self.__end is not None:
            way = 'nothing'
            if year < self.__start.year:
                way = 'before'
            if year > self.__end.year:
                way = 'after'
            if month < self.__start.month:
                way = 'before'
            if month > self.__end.month:
                way = 'after'
            if day < self.__start.day:
                way = 'before'
            if day > self.__end.day:
                way = 'after'
            if hour < self.__start.hour:
                way = 'before'
            if hour > self.__end.hour:
                way = 'after'
            if way == 'before':
                chosen = datetime(
                    year,
                    month if month is not None else 1,
                    day if day is not None else 1,
                    hour if hour is not None else 0
                )
                kwargs = {
                    'start': chosen.strftime('%Y-%m-%d %H:%M'),
                    'end': self.__start.strftime('%Y-%m-%d %H:%M')
                }
            elif way == 'after':
                chosen = datetime(
                    year,
                    month if month is not None else 12,
                    day if day is not None else 31,
                    hour if hour is not None else 23,
                    59, 59
                )
                kwargs = {
                    'start': self.__end.strftime('%Y-%m-%d %H:%M'),
                    'end': chosen.strftime('%Y-%m-%d %H:%M')
                }
            else:
                return
            resp = self.__session.request('list_events', **kwargs)
            if resp.status_code == 200:
                if way == 'before':
                    self.__start = chosen
                else:
                    self.__end = chosen
                with resp.json() as data:
                    for i in data:
                        self.__cal.append(Event(self.__session, i, data[i]))
        else:
            self.__start = datetime(
                year,
                month if month is not None else 1,
                day if day is not None else 1,
                hour if hour is not None else 0,
            )
            self.__end = datetime(
                year,
                month if month is not None else 12,
                day if day is not None else 31,
                hour if hour is not None else 23,
                59, 59
            )
            resp = self.__session.request(
                'list_events',
                start=self.__start.strftime('%Y-%m-%d %H:%M'),
                end=self.__end.strftime('%Y-%m-%d %H:%M')
            )
            if resp.status_code == 200:
                with resp.json() as data:
                    for i in data:
                        self.__cal.append(Event(self.__session, i, data[i]))

    def get_year(self, year: int):
        r = []
        for i in self.__cal:
            if i.starts.year <= year <= i.ends.year:
                r.append(i)
        return r

    def get_month(self, year: int, month: int):
        r = []
        for i in self.__cal:
            if i.starts.year <= year <= i.ends.year and i.starts.month <= month <= i.ends.month:
                r.append(i)
        return r

    def get_day(self, year: int, month: int, day: int):
        r = []
        for i in self.__cal:
            if i.starts.year <= year <= i.ends.year and i.starts.month <= month <= i.ends.month and i.starts.day <= day <= i.ends.day:
                r.append(i)
        return r

    def create(self, name: str, starts: str, ends: str, location: Location, alerts: list[str], repeat: str, travel_time: str, participants: list[str], notes: str, url: str, attachments: list[str]):
        self.__session.request(
            'create_event',
            object={
                'name': name,
                'starts': starts,
                'ends': ends,
                'location': {
                    'name': location.name,
                    'street': location.street,
                    'no': location.no,
                    'zipcode': location.zipcode,
                    'country': location.country
                },
                'alerts': alerts,
                'repeat': repeat,
                'travel_time': travel_time,
                'participants': participants,
                'notes': notes,
                'url': url,
                'attachments': attachments
            }
        )

    def get_event(self, id) -> (Event, None):
        for i in self.__cal:
            if i.id == id:
                return i
        resp = self.__session.request('get_event', id=id)
        if resp.status_code == 200:
            e = Event(self.__session, id, resp.json())
            self.__cal.append(e)
            return e
        else:
            return None
