import subprocess


@property
def __version__() -> float:
    out = subprocess.run(['pip', 'show', 'TheProtocols'], stdout=subprocess.PIPE)
    out = out.stdout.decode().split('\n')[1].split(' ')[1]
    return float(out.split('.')[0] + '.' + out.split('.')[1])
