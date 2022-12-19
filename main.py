import argparse
import logging
import multiprocessing as mp
import os
import random
import string
import time

import socketio
from tqdm import tqdm

from broker.app import init

logging.basicConfig(level=logging.INFO)

skills = {}


def set_skills(data):
    global skills
    if len(data) > 0:
        for skill in data:
            skills[skill['name']] = skill


def get_random_string(length):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="The url of the broker")
    parser.add_argument("--token", help="The token to authenticate at the broker")
    parser.add_argument("--skill", help="The skill name to test")
    parser.add_argument("--test", help="Execute a stress test", action="store_true")
    parser.add_argument("--n", help="Iterations in the stress test")
    parser.add_argument("--timeout", help="Max timeout in seconds for the stress test")
    parser.add_argument("--k", help="String length")
    parser.add_argument("--start_broker",
                        help="With this parameter an additional broker instance is stared in a separate thread "
                             "(make docker must run before)",
                        action="store_true")
    parser.set_defaults(
        url="http://{}:{}".format(os.getenv("BROKER_HOST"), os.getenv("BROKER_PORT")),
        token=os.getenv("BROKER_TOKEN"),
        skill="text_classification",
        test=False,
        n=10,
        k=10,
        timeout=20,
        start_broker=False
    )

    args = parser.parse_args()

    # start broker
    if args.start_broker:
        ctx = mp.get_context('spawn')
        broker = ctx.Process(target=init, args=())
        broker.start()

    sio = socketio.Client(reconnection_delay=1, reconnection=True, reconnection_attempts=100)


    @sio.on('connect')
    def connect():
        logging.info('Connection successful established!')
        sio.emit('skillGetAll')


    @sio.on('skillUpdate')
    def skills_update(data):
        logging.info('Received list of skills: {}'.format(data))
        set_skills(data)


    @sio.on('skillConfig')
    def config(data):
        logging.info('Received config: {}'.format(data))


    start_times = {}
    end_times = {}


    @sio.on('skillResults')
    def skill_results(data):
        global end_times
        if args.test:
            end_times[data['id']] = time.perf_counter()
        else:
            logging.info('Received results: {}'.format(data))


    # connect
    logging.info('Connecting to broker at {}'.format(args.url))
    while not sio.connected:
        try:
            sio.connect(args.url, auth={"token": args.token})
        except socketio.exceptions.ConnectionError:
            logging.error('Connection to broker failed!')
            time.sleep(1)
        time.sleep(2)

    if args.test:

        ctx = mp.get_context('spawn')
        container = ctx.Process(target=simple_response_container, args=(args.url, args.token, args.skill))
        container.start()

        logging.info("Waiting for container to start ...")
        while args.skill not in skills:
            time.sleep(0.1)

        ## Test simple response
        start_times["simple"] = time.perf_counter()
        sio.emit('skillRequest', {'id': "simple", 'name': args.skill, 'data': get_random_string(args.k)})
        while "simple" not in end_times:
            time.sleep(0.1)
        logging.info("Simple response time: {:3f}ms".format((end_times["simple"] - start_times["simple"]) * 1000))

        while True:
            print("Test")
            time.sleep(1)

        ## Test stress test
        quota = min(os.getenv("QUOTA_CLIENTS"), os.getenv("QUOTA_RESULTS"))
        with tqdm(total=int(args.n), desc="Sending requests") as pbar:
            for i in range(int(args.n)):
                sio.emit('skillRequest', {'id': i, 'name': args.skill, 'data': get_random_string(args.k)})

                start_times[i] = time.perf_counter()
                pbar.update(1)

                # Wait during quota
                time.sleep((1 / int(quota)) + 0.01)

            pbar.close()

        print("\nTotal time to send requests: {:.3f}ms\n".format((time.perf_counter() - start_times[0]) * 1000))

        # Wait for results
        with tqdm(total=int(args.n), desc="Receiving results") as pbar:
            while (len(end_times) - 1) < int(args.n) and (time.perf_counter() - start_times[0]) < int(args.timeout):
                pbar.update(n=len(end_times) - 1)
                time.sleep(0.5)
        pbar.close()

        for i in range(int(args.n)):
            if i not in end_times:
                print("Request {} timed out!".format(i))
            else:
                print("Request {} took {:.4f}ms".format(i, (end_times[i] - start_times[i]) * 1000))

    else:
        sio.emit('skillRequest',
                 {'id': 1, 'name': args.skill,
                  'data': get_random_string(args.k)})
