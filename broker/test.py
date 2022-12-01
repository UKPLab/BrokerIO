import socketio
import argparse
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--url",  help="The url of the broker")
    parser.add_argument("--token", help="The token to authenticate at the broker")
    parser.set_defaults(
        url="http://localhost:5672",
        token="TestToken"
    )

    args = parser.parse_args()
    sio = socketio.Client()

    @sio.on('connect')
    def connect():
        logging.info('Connection successful established!')
        sio.emit('get_info')

    @sio.on('info')
    def info(data):
        logging.info('Received info: {}'.format(data))

    sio.connect(args.url, auth={"token": args.token})
    sio.wait()
