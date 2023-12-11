import multiprocessing as mp
import os

from Crypto.PublicKey import RSA

from broker import load_config
from broker.utils import scrub_job, init_job
from broker.db import connect_db
from . import CLI


class Broker(CLI):
    def __init__(self):
        super().__init__()
        self.name = 'broker'
        self.help = "Menu for managing broker"
        self.assign_parser = None

    def set_parser(self, parser):
        self.parser = parser
        sub_parser = parser.add_subparsers(dest='sub_command', help="Commands for managing broker")
        sub_parser.add_parser('scrub', help="Start a scrub job - scrub database")
        sub_parser.add_parser('init', help="Reinit the default users (reading keys)")
        self.assign_parser = sub_parser.add_parser('assign', help="Assign a role to a user")
        self.assign_parser.add_argument('--role', help="Assign role to user (Default: admin)", type=str,
                                        default='admin')
        self.assign_parser.add_argument('--key', help="Public key of user for assigning a role",
                                        type=str, default=None)

    def handle(self, args):
        if args.sub_command == 'scrub':
            ctx = mp.get_context('spawn')
            scrub = ctx.Process(target=scrub_job)
            scrub.start()
            scrub.join()
        elif args.sub_command == 'init':

            self.check_key(create=True)

            ctx = mp.get_context('spawn')
            scrub = ctx.Process(target=init_job)
            scrub.start()
            scrub.join()
        elif args.sub_command == 'assign':
            if args.key is None or args.role is None:
                self.assign_parser.print_help()
                exit()

            config = load_config()
            config['cleanDbOnStart'] = False
            config['scrub']['enabled'] = False
            config['taskKiller']['enabled'] = False
            db = connect_db(config, None)

            user = db.users.set_role(args.key, args.role)
            if user:
                print("Role assigned to user, db entry: {}".format(user['_key']))
            else:
                print("User not found in db, please check the public key")


        else:
            self.parser.print_help()
            exit()

    def check_key(self, private_key_path="private_key.pem", length=1024, create=False):
        """
        Check if key file exists
        :param private_key_path: path to key file
        :param length: length of key
        :param create: create key if not exists
        :return:
        """
        if not os.path.exists(private_key_path):
            if create:
                key = RSA.generate(length)
                with open(private_key_path, "wb") as f:
                    f.write(key.export_key("PEM"))
                    print("Key written to {}".format(private_key_path))
            else:
                print("Key file not found: {}".format(private_key_path))
                exit(1)
        else:
            print("Key file found: {}".format(private_key_path))
