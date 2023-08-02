import argparse
import logging
import multiprocessing as mp
import os

from broker import init_logging, load_config
from broker.utils import scrub_job, init_job
from broker.db import connect_db

from test.TestClient import TestClient


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Broker URL", default=os.getenv("BROKER_URL", "http://localhost:4852"))
    parser.add_argument("--skill", help="Skill name to test", default="test_skill")
    parser.add_argument("--scrub", help="Start a scrub job", type=bool)
    parser.add_argument("--init", help="Reinit the default users (reading keys)", type=bool)
    parser.add_argument('--role', help="Assign role to user (only if assign_role is set to true)", type=str,
                        default='admin')
    parser.add_argument('--key', help="Public key of user for assigning a role (only if assign_role is set to true)",
                        type=str, default=None)
    parser.add_argument('--assign_role', help="Assign role to user", type=bool, default=False)
    return parser


if __name__ == '__main__':
    logger = init_logging("ClientTester", logging.DEBUG)
    args = args().parse_args()

    if args.assign_role:
        if args.key is None:
            print("Please provide a public key for assigning a role")
            exit(1)

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

    elif args.scrub:
        ctx = mp.get_context('spawn')
        scrub = ctx.Process(target=scrub_job)
        scrub.start()
        scrub.join()
    elif args.init:
        ctx = mp.get_context('spawn')
        scrub = ctx.Process(target=init_job)
        scrub.start()
        scrub.join()
    else:
        client = TestClient(logger, args.url, args.skill, queue_size=10)
        client.start()

        client.put({"id": "1", "name": args.skill,
                    "data": {"text": "Rewrite this section to explain how this file fits into the project."}})

        while True:
            print(client.get())
