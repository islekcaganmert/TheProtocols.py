from TheProtocols.helpers.exceptions import CredentialsDidntWorked
from TheProtocols.objects.app import App
from TheProtocols.session import Session
from typing import Any


class Permission:
    class ID:
        RSA = "RSA"
        HiddenInformation = "HiddenInformation"
        ModifyID = "ModifyID"

    class Contacts:
        Read = "Contacts"
        Write = "ContactsWrite"

    class Reminders:
        Read = "Reminders"
        Write = "RemindersWrite"

    class Mail:
        Box = "Mail"
        Send = "MailSend"

    class Notes:
        Read = "Notes"
        Write = "NotesWrite"

    class IoT:
        Limited = "IoT"
        Full = "IoT-Full"

    class Filesystem:
        Read = "ReadFile"
        Write = "WriteFile"

    Search = "Search"
    Feed = "Feed"
    Chat = "Chat"
    Calendar = "Calendar"
    Events = "Events"
    InterApp = "InterApp"


class TheProtocols(App):
    def __init__(self, package_name, permissions, secure: bool = True):
        super().__init__(package_name, secure)
        self.permissions = permissions
        self.__cache = []

    def create_session(self, email, password) -> (Session, None):
        try:
            r = Session(self, email, password)
            if r.token is None and r.network.version >= 3.1:
                return None
            else:
                return r
        except CredentialsDidntWorked:
            return None

    def restore_session(self, email, token) -> (Session, None):
        return Session(self, email, None, token=token)

    def get_cached(self, obj, key, value, s) -> (Any, None):
        for i in self.__cache:
            if isinstance(i, obj):
                if getattr(i, key) == value:
                    return i
        self.__cache.append(obj(**{key: value, 's': s}))
        return self.__cache[-1]
