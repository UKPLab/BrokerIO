from flask import session

from broker.sockets import Socket


class Request(Socket):
    """
    Basic socket.io event handlers for authentication

    @author: Dennis Zyska
    """

    def __init__(self, db, socketio):
        super().__init__("skill", db, socketio)

    def _init(self):
        self.socketio.on_event("skillRequest", self.request)
        self.socketio.on_event("taskResults", self.results)
        self.socketio.on_event("taskAbort", self.abort)

    def request(self, data):
        """
        Request a specific skill by name
        """
        try:
            if self.db.clients.quota(session["sid"], append=True):
                self.socketio.emit("error", {"code": 100}, to=session["sid"])
                return

            # get a node that provides this skill
            node = self.db.skills.get_node(session["sid"], data["name"])
            if node is None:
                self.socketio.emit("error", {"code": 200}, to=session["sid"])
            else:
                # check if the client has enough quota to run this job
                if self.db.clients.quota(session["sid"], append=False, is_job=True):
                    self.socketio.emit("error", {"code": 101}, to=session["sid"])
                    return

                task = self.db.tasks.create(session["sid"], node, data)
                self.socketio.emit("taskRequest", {'id': task['_key'], 'data': data['data']}, room=node)
                self.db.clients.quotas[session["sid"]]["jobs"].append(task['_key'])
        except:
            self.logger.error("Error in request {}: {}".format("skillRequest", data))
            self.socketio.emit("error", {"code": 500}, to=session["sid"])

    def results(self, data):
        """
        Send results to client
        """
        try:
            node = session["sid"]
            if self.db.clients.quota(node, append=True, is_result=True):
                return

            if type(data) is dict and "id" in data and "data" in data:
                self.db.tasks.update(data["id"], node, data)
        except:
            self.logger.error("Error in request {}: {}".format("taskResults", data))
            self.socketio.emit("error", {"code": 500}, to=session["sid"])

    def abort(self, data):
        """
        Send results to client
        """
        try:
            if self.db.clients.quota(session["sid"], append=True):
                self.socketio.emit("error", {"code": 100}, to=session["sid"])
                return

            self.db.tasks.abort_by_user(data["id"], session["sid"])
        except:
            self.logger.error("Error in request {}: {}".format("taskKilled", data))
            self.socketio.emit("error", {"code": 500}, to=session["sid"])
