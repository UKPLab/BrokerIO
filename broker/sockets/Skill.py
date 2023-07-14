import json

from flask import session

from broker.sockets import Socket


class Skill(Socket):
    """
    Basic socket.io event handlers for authentication

    @author: Dennis Zyska
    """

    def __init__(self, db, socketio):
        super().__init__("skill", db, socketio)

    def _init(self):
        self.socketio.on_event("skillRegister", self.register)
        self.socketio.on_event("skillGetAll", self.get_all)
        self.socketio.on_event("skillGetConfig", self.get_config)

    def get_config(self, data):
        """
        Get configuration from a skill by name
        """
        try:
            if self.clients.quota(session["sid"], append=True):
                return

            self.skills.send_update(data['name'], with_config=True, to=session["sid"])
        except:
            self.logger.error("Error in request {}: {}".format("skillGetConfig", data))
            self.socketio.emit("error", {"code": 500}, to=session["sid"])

    def get_all(self):
        """
        Informs the client about all skills currently registered on the broker.

        This should be called after a client connects to the broker. Further updates are provided by the
        "skillRegister" event.
        """
        try:
            if self.clients.quota(session["sid"], append=True):
                return

            self.skills.send_update(to=session["sid"])
        except:
            self.logger.error("Error in request {}".format("skillGetAll"))
            self.socketio.emit("error", {"code": 500}, to=session["sid"])

    def register(self, data):
        """
        Registers a skill on the broker.

        :param data: Data Object
        """
        try:
            if isinstance(data, str):  # needed for c++ socket.io client
                data = json.loads(data)

            if self.clients.quota(session["sid"], append=True):
                return

            self.skills.register(session["sid"], data)
        except:
            self.logger.error("Error in request {}: {}".format("skillRegister", data))
            self.socketio.emit("error", {"code": 500}, to=session["sid"])
