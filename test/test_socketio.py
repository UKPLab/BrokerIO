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
        time.sleep(5)

        sio.disconnect()

        self.assertTrue(connected)

    def ignore_test_simple(self):
        result = []

        def set_result(r):
            nonlocal result
            result += [r]

        sio = socketio.Client()
        sio.on("celery-result", set_result)

        sio.connect("http://localhost:4852")
        connected = sio.sid is not None
        sio.emit("register_skill", {"uid": "uid", "name": "someskill", "config": "config", })
        time.sleep(20)

        self.assertTrue(len(result) == 1)

        sio.disconnect()

        self.assertTrue(connected)


if __name__ == '__main__':
    unittest.main()
