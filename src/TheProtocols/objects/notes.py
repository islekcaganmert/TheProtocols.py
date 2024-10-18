from TheProtocols.helpers.exceptions import NoteNotFound
from TheProtocols.objects.deleted import Deleted


class Notes:
    def __init__(self, id) -> None:
        self.id = id
        r = self.id.request('pull_notes')
        if r.status_code == 200:
            self.fs = r.json()
        else:
            self.fs = {}

    def get(self, filename: str) -> str:
        r = self.fs
        try:
            for i in filename.split('/'):
                if i != '':
                    r = r[i]
        except Exception as e:
            raise NoteNotFound(e)
        if isinstance(r, str):
            return r
        else:
            raise NoteNotFound(filename)

    def edit(self, filename: str, content: str) -> bool:
        r = self.id.request('edit_note', path=filename, value=content)
        if r.status_code == 200:
            self.__init__(self.id)
            return True
        else:
            return False

    def delete(self, filename: str) -> bool:
        return self.edit(filename, Deleted)
