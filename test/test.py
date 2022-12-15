import argparse
import logging
import random
import string
import time

import socketio
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
skills = None
starts = []
end_times = {}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="The url of the broker")
    parser.add_argument("--token", help="The token to authenticate at the broker")
    parser.add_argument("--skill", help="The skill name to test")
    parser.add_argument("--test", help="Execute a stress test", action="store_true")
    parser.add_argument("--n", help="Iterations in the stress test")
    parser.add_argument("--timeout", help="Max timeout in seconds for the stress test")
    parser.set_defaults(
        url="http://localhost:4852",
        token="this_is_a_random_token_to_verify",
        skill=None,
        test=False,
        n=10,
        timeout=20
    )

    args = parser.parse_args()
    sio = socketio.Client()


    @sio.on('connect')
    def connect():
        logging.info('Connection successful established!')
        sio.emit('skillGetAll')


    @sio.on('skillUpdate')
    def skills_update(data):
        global skills
        logging.info('Received list of skills: {}'.format(data))
        sio.emit('skillGetConfig', {'name': data[0]['name']})
        skills = data


    @sio.on('skillConfig')
    def config(data):
        logging.info('Received config: {}'.format(data))


    @sio.on('skillResults')
    def skill_results(data):
        global starts, end_times
        if args.test:
            end_times[data['id']] = time.perf_counter()
        else:
            logging.info('Received results: {}'.format(data))


    sio.connect(args.url, auth={"token": args.token})
    time.sleep(2)

    # Waiting for connection
    while not sio.connected:
        time.sleep(1)

    if args.test:

        with tqdm(total=int(args.n)) as pbar:
            results = 0
            for i in range(int(args.n)):
                text = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
                sio.emit('skillRequest',
                         {'id': i, 'name': skills[0]['name'] if args.skill is None else args.skill,
                          'data': text})
                starts.append(time.perf_counter())
                pbar.update(1)
                time.sleep(0.04)

            pbar.close()

        time.sleep(1)
        print("\nTotal time to send requests: {:.4f}ms\n".format((time.perf_counter() - starts[0]) * 1000))

        pbar = tqdm(total=int(args.n), desc="Results")
        timeout = time.time()
        while len(end_times) < int(args.n):
            time.sleep(1)
            pbar.update(n=len(end_times))
            if time.time() > (timeout + args.timeout):
                break
        pbar.update(n=len(end_times))
        pbar.close()

        for i in range(int(args.n)):
            if i not in end_times:
                print("Request {} timed out!".format(i))
            else:
                print("Request {} took {:.4f}ms".format(i, (end_times[i] - starts[i]) * 1000))

    else:
        while True:
            new_input = input("Send string to broker as new task: ")
            sio.emit('skillRequest',
                     {'id': 1, 'name': skills[0]['name'] if args.skill is None else args.skill, 'data': new_input})
