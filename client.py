import argparse
import logging
import multiprocessing as mp
import os

from broker.utils import init_logging
from broker.utils import scrub_job
from test.TestClient import TestClient


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Broker URL", default=os.getenv("BROKER_URL", "http://localhost:4852"))
    parser.add_argument("--token", help="Broker Token",
                        default=os.getenv("BROKER_TOKEN", "this_is_a_random_token_to_verify"))
    parser.add_argument("--skill", help="Skill name to test", default="test_skill")
    parser.add_argument("--scrub", help="Start a scrub job", type=bool)
    return parser


if __name__ == '__main__':
    logger = init_logging("ClientTester", logging.DEBUG)
    args = args().parse_args()

    if args.scrub:
        ctx = mp.get_context('spawn')
        scrub = ctx.Process(target=scrub_job)
        scrub.start()
        scrub.join()
    else:
        client = TestClient(logger, args.url, args.token, args.skill, queue_size=10)
        client.start()

        client.put({"id": "1", "name": args.skill,
                    "data": {"text": "Rewrite this section to explain how this file fits into the project."}})

        while True:
            print(client.get())
