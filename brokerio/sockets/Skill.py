import json

from . import Socket


class Skill(Socket):
    """
    Basic socket.io event handlers for authentication

    @author: Dennis Zyska
    """

    def __init__(self, db, socketio):
        super().__init__("skill", db, socketio)

    def _init(self):
        self.socketio.on("skillRegister", self.register)
        self.socketio.on("skillGetAll", self.get_all)
        self.socketio.on("skillGetConfig", self.get_config)

    async def get_config(self, sid, data):
        """
        Get configuration from a skill by name
        """
        try:
            if self.db.clients.quota(sid, append=True):
                await self.socketio.emit("error", {"code": 100}, to=sid)
                return

            client = self.db.clients.get(sid)
            skills = self.db.skills.get_skills(filter_role=client["role"], filter_name=data["name"], with_config=True)

            if len(skills) == 0:
                await self.socketio.emit("error", {"code": 203}, to=sid)
                return

            await self.socketio.emit("skillConfig", skills[0]['config'], to=sid)
        except Exception as e:
            self.logger.error("Error in request {}: {}".format("skillGetConfig", data))
            self.logger.error(e)
            await self.socketio.emit("error", {"code": 500}, to=sid)

    async def get_all(self, sid):
        """
        Informs the client about all skills currently registered on the broker.

        This should be called after a client connects to the broker. Further updates are provided by the
        "skillRegister" event.
        """
        try:
            if self.db.clients.quota(sid, append=True):
                await self.socketio.emit("error", {"code": 100}, to=sid)
                return

            client = self.db.clients.get(sid)

            await self.db.skills.send_all(role=client['role'], to=sid)
        except Exception as e:
            self.logger.error("Error in request {}".format("skillGetAll"))
            self.logger.error(e)
            await self.socketio.emit("error", {"code": 500}, to=sid)

    async def register(self, sid, data):
        """
        Registers a skill on the broker.

        :param data: Data Object
        """
        try:
            if isinstance(data, str):  # needed for c++ socket.io client
                data = json.loads(data)

            if self.db.clients.quota(sid, append=True):
                return

            if 'name' in data:
                await self.db.skills.register(sid, data)
            else:
                await self.socketio.emit("error", {"code": 202}, to=sid)
        except Exception as e:
            self.logger.error("Error in request {}: {}".format("skillRegister", data))
            self.logger.error(e)
            await self.socketio.emit("error", {"code": 500}, to=sid)
