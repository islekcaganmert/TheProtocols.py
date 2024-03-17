import requests

authority = 'aas.hereus.net'


def get(addr: str) -> str:
    r = requests.post(f"https://{authority}/protocols/aas/get", json={'domain': addr})
    if r.status_code == 200:
        d = r.content.decode('UTF-8')
    else:
        d = addr
    return d
