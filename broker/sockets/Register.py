from flask import session


class Register:
    """
    Basic socket.io event handlers for skill and task management

    @author: Dennis Zyska, Nils Dycke
    """

    def __init__(self, socketio, skills, tasks, clients):
        self.socketio = socketio
        self.tasks = tasks
        self.skills = skills
        self.clients = clients

        self._init()

    def _init(self):
        self.socketio.on_event("skillRegister", self.register)
        self.socketio.on_event("skillGetAll", self.get_all)
        self.socketio.on_event("skillGetConfig", self.get_config)
        self.socketio.on_event("skillRequest", self.request)
        self.socketio.on_event("taskResults", self.results)

    def register(self, data):
        """
        Registers a skill on the broker.

        :param data: Data Object
        """
        if self.clients.check_quota(session["sid"], append=True):
            return

        self.skills.register(session["sid"], data)

    def get_all(self):
        """
        Informs the client about all skills currently registered on the broker.

        This should be called after a client connects to the broker. Further updates are provided by the
        "skillRegister" event.
        """
        if self.clients.check_quota(session["sid"], append=True):
            return

        self.skills.send_update(to=session["sid"])

    def get_config(self, data):
        """
        Get configuration from a skill by name
        """
        if self.clients.check_quota(session["sid"], append=True):
            return

        self.skills.send_update(data['name'], with_config=True, to=session["sid"])

    def request(self, data):
        """
        Request a specific skill by name
        """
        if self.clients.check_quota(session["sid"], append=True):
            return

        # get all available nodes for skill; get a random owner from the list
        node = self.skills.get_node(data["name"])
        if node is None:
            self.socketio.emit("requestError", {"error": "No node for this skill available!"}, to=session["sid"])
        else:
            # cache requests
            task = self.tasks.create(session["sid"], node, data)
            # request skill of the owner
            self.socketio.emit("taskRequest", {'id': task['_key'], 'data': data['data']}, room=node)

    def results(self, data):
        """
        Send results to client
        """
        node = session["sid"]
        if self.clients.check_quota(node, append=True, results=True):
            return

        if type(data) is dict and "id" in data and "data" in data:
            self.tasks.finish(data["id"], node, data)
