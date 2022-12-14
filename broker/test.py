import socketio
import argparse
import logging
import time

logging.basicConfig(level=logging.INFO)
skills = None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="The url of the broker")
    parser.add_argument("--token", help="The token to authenticate at the broker")
    parser.set_defaults(
        url="http://localhost:4852",
        token="this_is_a_random_token_to_verify"
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
    def results(data):
        logging.info('Received config: {}'.format(data))

    sio.connect(args.url, auth={"token": args.token})

    while True:
        time.sleep(5)
        new_input = input("Send string to broker as new task: ")
        sio.emit('skillRequest', {'id': 1, 'name': skills[0]['name'], 'data': new_input})
