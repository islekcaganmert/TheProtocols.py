from .Objects import Mail


class Mailbox:
    def __init__(self, user, name: str, last_index: int) -> None:
        self.__as = user
        self.__last = last_index
        self.__name = name

    def get_mail(self, id: int) -> Mail:
        return Mail(self.__as, self.__name, id)
