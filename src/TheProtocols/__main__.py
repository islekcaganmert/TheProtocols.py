import json
import sys
import os
from TheProtocols import *
import getpass


# noinspection PyDefaultArgument
def main(args: list = sys.argv[1:]):
    if args[0] == 'dev':
        if args[1] == 'signature':
            package_name = args[2] if len(args) > 2 else input('Package: ')
            s: Session = TheProtocols(
                package_name=package_name,
                permissions=["RSA"]
            ).create_session(
                input('Email: ') if 'EMAIL' not in os.environ else os.environ.get('EMAIL'),
                getpass.getpass()
            )
            print(s.network.version)
            print(s.sign(json.dumps({
                "package": package_name,
                "permissions": args[3].split(',') if len(args) > 3 else input('Permissions: ').split(',')
            })))


if __name__ == '__main__':
    main()
