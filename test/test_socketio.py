import time
import unittest
import socketio


class TestSocketIO(unittest.TestCase):
    def test_connect(self):
        sio = socketio.Client()
        sio.connect("http://localhost:4852", auth={"token": "this_is_a_random_token_to_verify"})
        connected = sio.sid is not None
        sio.disconnect()

        self.assertTrue(connected)

    def test_register_skill(self):
        with open("resources/test.yaml", "r") as f:
            config = f.read()

        print(f"Testing register with mock config:\n{config}")

        sio = socketio.Client()

        sio.connect("http://localhost:4852", auth={"token": "this_is_a_random_token_to_verify"})
        connected = sio.sid is not None

        sio.emit("register_skill",
                 {"uid": "stance_classifier1",
                  "name": "stance_classification",
                  "config": config})
        time.sleep(1)

        sio.disconnect()

        self.assertTrue(connected)

    def test_get_info(self):
        with open("resources/test.yaml", "r") as f:
            config = f.read()

        sio = socketio.Client(logger=True, engineio_logger=True)

        @sio.on("info")
        def check_result(r):
            print(r)

            self.assertTrue(r is not None)
            sio.disconnect()

        @sio.on("*")
        def any_message(m):
            print(m)

            sio.disconnect()

        sio.connect("http://localhost:4852", auth={"token": "this_is_a_random_token_to_verify"})
        self.assertTrue(sio.sid is not None)

        sio.emit("register_skill",
                 {"uid": "stance_classifier1",
                  "name": "stance_classification",
                  "config": config})

        sio.emit("get_info")

        print("Waiting for info")
        print(sio.handlers)
        sio.wait()


if __name__ == '__main__':
    unittest.main()
