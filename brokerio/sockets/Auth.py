from Crypto.Hash import SHA256

from . import Socket
from ..utils.Keys import verify


class Auth(Socket):
    """
    Basic socket.io event handlers for authentication

    @author: Dennis Zyska
    """

    def __init__(self, db, socketio):
        super().__init__("skill", db, socketio)

    def _init(self):
        self.socketio.on("authRequest", self.request)
        self.socketio.on("authResponse", self.response)
        self.socketio.on("authStatus", self.status)

    async def response(self, sid, data):
        """
        Register as a client, receive public key and associate with user
        :param data: object with public key and signature {pub:...,sig:...}
        :return:
        """
        try:
            if self.db.clients.quota(sid, append=True):
                await self.socketio.emit("error", {"code": 100}, to=sid)
                return
            client = self.db.clients.get(sid)
            if "secret" in client:
                if verify(client['secret'], data['sig'], data['pub']):
                    user = self.db.users.auth(sid, data['pub'])
                    user = self.db.users.get(user['_key'])
                    client['user'] = user['_key']

                    # updating client role
                    client['role'] = user['role']
                    await self.socketio.leave_room(sid, "role:guests")
                    await self.socketio.enter_room(sid, "role:{}".format(user['role']))

                    # send skill updates as role changed
                    await self.db.skills.send_all(role=user['role'], to=sid)

                    self.db.clients.save(client)
                    await self.status(sid)
                else:
                    self.logger.error("Error in verify {}: {}".format(sid, data))
                    await self.socketio.emit("error", {"code": 401}, to=sid)
            else:
                self.request()
        except Exception as e:
            self.logger.error("Error in request {}: {}".format("authRegister", data))
            self.logger.error(e)
            await self.socketio.emit("error", {"code": 500}, to=sid)

    async def request(self, sid, data=None):
        """
        Authenticate a user, assign client to user
        :param data: object with public and signature
        :return:
        """
        try:
            if self.db.clients.quota(sid, append=True):
                await self.socketio.emit("error", {"code": 100}, to=sid)
                return
            # create secret message to sign by client
            secret_message = "{}{}".format(sid, "awesomesecret")
            hash = SHA256.new()
            hash.update(secret_message.encode("utf8"))
            self.db.clients.register(sid, hash.hexdigest())
            await self.socketio.emit("authChallenge", {"secret": hash.hexdigest()})
        except Exception as e:
            self.logger.error("Error in request {}".format("authRequest"))
            self.logger.error(e)
            await self.socketio.emit("error", {"code": 500}, to=sid)

    async def status(self, sid, data=None):
        """
        Send current authentication status
        :return:
        """
        try:
            if self.db.clients.quota(sid, append=True):
                await self.socketio.emit("error", {"code": 100}, to=sid)
                return
            client = self.db.clients.get(sid)
            if "user" in client:
                user = self.db.users.get(client['user'])
                if user:
                    await self.socketio.emit("authInfo", {"role": user['role']}, to=sid)
                else:
                    await self.socketio.emit("authInfo", {"role": "guest"}, to=sid)
            else:
                await self.socketio.emit("authInfo", {"role": "guest"}, to=sid)
        except Exception as e:
            self.logger.error("Error in request {}.".format("authStatus"))
            self.logger.error(e)
            await self.socketio.emit("error", {"code": 500}, to=sid)
