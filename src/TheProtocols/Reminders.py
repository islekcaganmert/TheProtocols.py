from .ID import ID
from .Objects import Reminder
import json
from datetime import datetime


class Reminders:
    def __init__(self, id: ID) -> None:
        self.id = id
        r = self.id.request('get_reminders')
        self.__fs = {}
        if r.status_code == 200:
            d = r.json()
            for a in d:
                self.__fs.update({a: []})
                for b in d[a]:
                    self.__fs[a].append(Reminder(b))

    def get_list(self, name: str) -> list[Reminder]:
        return self.__fs[name]

    def toggle_reminder(self, list: str, id: int) -> bool:
        r = self.id.request('toggle_reminder', list=list, id=id)
        if r.status_code == 200:
            self.__init__(self.id)
            return True
        else:
            return False

    def edit_reminder(self, list: str, id: int, **data) -> bool:
        d = json.loads(self.get_list(list)[id].json())
        for i in data:
            d[i] = data[i]
        r = self.id.request('edit_reminder', list=list, id=id, data=json.dumps(d))
        if r.status_code == 200:
            self.__init__(self.id)
            return True
        else:
            return False

    def delete_reminder(self, list: str, id: int) -> bool:
        r = self.id.request('delete_reminder', list=list, id=id)
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

    def create_reminder(self, list: str, title: str, deadline: str, repeat: str) -> bool:
        try:
            datetime.strptime(deadline, '%Y-%m-%d %H:%M')
        except Exception:
            raise ValueError('Deadline is not in correct format')
        r = self.id.request('create_reminder', list=list, title=title, deadline=deadline, repeat=repeat)
        if r.status_code == 200:
            self.__init__(self.id)
            return True
        else:
            return False

    def create_sub_reminder(self, list: str, reminder: str, title: str, deadline: str) -> bool:
        try:
            datetime.strptime(deadline, '%Y-%m-%d %H:%M')
        except Exception:
            raise ValueError('Deadline is not in correct format')
        r = self.id.request('create_sub_reminder', list=list, reminder=reminder, title=title, deadline=deadline)
        if r.status_code == 200:
            self.__init__(self.id)
            return True
        else:
            return False
