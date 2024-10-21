from datetime import datetime
import json


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
        try:
            self.deadline = datetime.strptime(d['deadline'], '%Y-%m-%d %H:%M')
        except ValueError:
            self.deadline = None
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


class Reminders:
    def __init__(self, id) -> None:
        self.id = id
        r = self.id.request('get_reminders')
        self.__fs = {}
        if r.status_code == 200:
            d = r.json()
            for a in d:
                self.__fs.update({a: []})
                for b in d[a]:
                    self.__fs[a].append(Reminder(b))

    @property
    def lists(self) -> list[str]:
        return list(self.__fs.keys())

    def get_list(self, name: str) -> list[Reminder]:
        return self.__fs[name]

    def toggle_reminder(self, lst: str, id: int) -> bool:
        r = self.id.request('toggle_reminder', list=lst, id=id)
        if r.status_code == 200:
            self.__init__(self.id)
            return True
        else:
            return False

    def edit_reminder(self, lst: str, id: int, **data) -> bool:
        d = json.loads(self.get_list(lst)[id].json())
        for i in data:
            d[i] = data[i]
        r = self.id.request('edit_reminder', list=lst, id=id, data=json.dumps(d))
        if r.status_code == 200:
            self.__init__(self.id)
            return True
        else:
            return False

    def delete_reminder(self, lst: str, id: int) -> bool:
        r = self.id.request('delete_reminder', list=lst, id=id)
        if r.status_code == 200:
            self.__init__(self.id)
            return True
        else:
            return False

    def create_list(self, name: str) -> bool:
        r = self.id.request('create_reminder_list', list=name)
        if r.status_code == 200:
            self.__init__(self.id)
            return True
        else:
            return False

    def create_reminder(self, lst: str, title: str, deadline: str, repeat: str) -> bool:
        try:
            datetime.strptime(deadline, '%Y-%m-%d %H:%M')
        except Exception:
            raise ValueError('Deadline is not in correct format')
        r = self.id.request('create_reminder', list=lst, title=title, deadline=deadline, repeat=repeat)
        if r.status_code == 200:
            self.__init__(self.id)
            return True
        else:
            return False

    def create_sub_reminder(self, lst: str, reminder: str, title: str, deadline: str) -> bool:
        try:
            datetime.strptime(deadline, '%Y-%m-%d %H:%M')
        except Exception:
            raise ValueError('Deadline is not in correct format')
        r = self.id.request('create_sub_reminder', list=lst, reminder=reminder, title=title, deadline=deadline)
        if r.status_code == 200:
            self.__init__(self.id)
            return True
        else:
            return False
