class Mail:
    def __init__(self, session, mailbox: str, id: int):
        self.__session = session
        self.__mailbox = mailbox
        self.__id = id
        resp = self.__session.request('get_mail', mailbox=self.__mailbox, id=self.__id)
        if resp.status_code == 200:
            data = resp.json()
            self.subject = data['subject']
            self.date_received = data['date_received']
            self.sender = data['sender']
            self.to = data['to']
            self.cc = data['cc']
            self.hashtag = data['hashtag']
            self.body = data['body']
        else:
            self.subject = None
            self.date_received = None
            self.sender = None
            self.to = None
            self.cc = None
            self.hashtag = None
            self.body = None

    def move(self, mailbox: str) -> bool:
        r = self.__session.request('move_mail', mailbox=self.__mailbox, id=self.__id, move_to=mailbox)
        if r.status_code == 200:
            for i in ['subject', 'date_received', 'sender', 'to', 'cc', 'hashtag', 'body']:
                setattr(self, i, None)
            self.__mailbox = self.__session = self.__id = None
            return True
        else:
            return False

    def delete(self) -> bool:
        return self.move('-')

    def trash(self) -> bool:
        return self.move('Trash')

    def archive(self) -> bool:
        return self.move('Archive')

    def __str__(self) -> str:
        return str(self.__id)
    __repr__ = __str__

    @property
    def mailbox(self) -> str:
        return self.__mailbox


class Mailbox:
    def __init__(self, session, name: str, mlist: int = None):
        self.__session = session
        self.__name = name
        self.__mails = None
        self.sync(mlist)

    def __str__(self) -> str:
        return self.__name
    __repr__ = __str__

    def sync(self, mlist: int = None):
        if mlist is None:
            resp = self.__session.request('list_mailboxes')
            if resp.status_code != 200:
                return
            mlist = resp.json()
        if not isinstance(mlist, int):
            mlist = mlist[str(self)]
        self.__mails = [Mail(self.__session, self.__name, i) for i in range(0, mlist + 1)]

    @property
    def mails(self) -> list[Mail]:
        return self.__mails
