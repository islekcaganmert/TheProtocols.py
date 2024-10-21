from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
import requests
from TheProtocols.objects.network import Network
from TheProtocols.objects.deleted import Deleted


def get_if_not_hidden(val) -> str:
    return val if str(val).replace('*', '') != '' else None


class User:
    def __init__(self, email: str, fetch_as=None, secure: bool = True) -> None:
        self.__email = lambda: email
        self.network = Network(email.split('@')[1], secure=secure)
        r = requests.get(self.network.protocol("user_info"), json={'username': email.split('@')[0]})
        self.rsa_private_key = None
        self.settings = {}
        if r.status_code == 200:
            d = r.json()
            self.name = get_if_not_hidden(d['name'])
            self.surname = get_if_not_hidden(d['surname'])
            self.country = get_if_not_hidden(d['country'])
            self.birthday = get_if_not_hidden(d['birthday'])
            self.rsa_public_key = get_if_not_hidden(d['rsa_public_key'])
            self.gender = get_if_not_hidden(d['gender'])
            self.phone_number = get_if_not_hidden(d['phone_number'])
            self.plus = get_if_not_hidden(d['plus'])
            self.timezone = get_if_not_hidden(d['timezone'])
            self.postcode = get_if_not_hidden(d['postcode'])
            self.profile_photo = get_if_not_hidden(d['profile_photo'])
            self.relation = ''
            self.socials = []
            self.fetch_as = fetch_as
            if fetch_as is not None:
                r = fetch_as.request('list_contacts').json().get(email, {'Relation': '', 'Socials': [], 'Error': True})
                if r.get('Error', False):
                    self.add = self.__add
                self.relation = r['Relation']
                self.socials = r['Socials']

    def json(self) -> dict:
        return {
            'name': self.name,
            'surname': self.surname,
            'country': self.country,
            'birthday': self.birthday,
            'rsa_public_key': self.rsa_public_key,
            'gender': self.gender,
            'phone_number': self.phone_number,
            'plus': self.plus,
            'timezone': self.timezone,
            'postcode': self.postcode,
            'profile_photo': self.profile_photo
        }

    def save(self) -> bool:
        if self.fetch_as is not None:
            r = self.fetch_as.request('edit_contact', email=str(self), data=self.json())
            return r.status_code == 200

    def __add(self, relation: str, socials: list[str]) -> bool:
        if self.fetch_as is not None:
            r = self.fetch_as.request('add_contact', email=str(self), relation=relation, socials=socials)
            return r.status_code == 200
        else:
            return False

    def delete(self) -> bool:
        if self.fetch_as is not None:
            r = self.fetch_as.request('edit_contact', email=str(self), data=Deleted)
            return r.status_code == 200
        else:
            return True

    def __str__(self) -> str:
        if self.country in ['CN', 'JP', 'KP', 'KR', 'TW', 'VN', 'TH', 'KH', 'LA']:
            return f"{self.surname} {self.name}"
        else:
            return f"{self.name} {self.surname}"

    def verify(self, signature: str, data: str) -> bool:
        rsa = serialization.load_pem_public_key(self.rsa_public_key.encode(), default_backend())
        try:
            rsa.verify(
                bytes.fromhex(signature),
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA512()
            )
            return True
        except InvalidSignature:
            return False

    __repr__ = __str__

    @property
    def email(self) -> str:
        return self.__email()
