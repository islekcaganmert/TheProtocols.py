from TheProtocols.objects.app import App
from TheProtocols.session import Session


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
    def __init__(self, package_name, application_token, permissions, secure: bool = True):
        super().__init__(package_name, secure)
        self.application_token = application_token
        self.permissions = permissions

    def create_session(self, email, password) -> (Session, None):
        r = Session(self, email, password)
        if r.token is None and r.network.version >= 3.1:
            return None
        else:
            return r
