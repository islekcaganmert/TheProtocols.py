from TheProtocols import ID
from getpass import getpass

email = input('Email Address: ')
password = getpass('Password: ')

user = ID(email, password)
print(f"{user.id} <{user}>")

for i in user.chats():
    print(i.get_chat_history())
