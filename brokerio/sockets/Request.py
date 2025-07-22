import numpy as np

from . import Socket


class Request(Socket):
    """
    Basic socket.io event handlers for authentication

    @author: Dennis Zyska
    """

    def __init__(self, db, socketio):
        super().__init__("skill", db, socketio)

    def _init(self):
        self.socketio.on("skillRequest", self.request)
        self.socketio.on("taskResults", self.results)
        self.socketio.on("taskUpdate", self.results)
        self.socketio.on("requestAbort", self.abort)

    async def request(self, sid, data):
        """
        Request a specific skill by name
        """
        try:
            if "id" not in data or "name" not in data:
                await self.socketio.emit("error", {"id": data['id'] if 'id' in data else None, "code": 113}, to=sid)
                return
            if self.db.clients.quota(sid, append=True):
                await self.socketio.emit("error", {"id": data['id'] if 'id' in data else None, "code": 100},
                                   to=sid)
                return

            # get a node that provides this skill
            node = self.db.skills.get_node(sid, data["name"])
            if node is None:
                await self.socketio.emit("error", {"id": data['id'] if 'id' in data else None, "code": 200}, to=sid)
            else:
                # check if the client has enough quota to run this job
                reserve_quota = np.random.randint(1000000, 2 ** 31 - 1)
                if self.db.clients.quota(sid, append=reserve_quota, is_job=True):
                    await self.socketio.emit("error", {"id": data['id'] if 'id' in data else None, "code": 101}, to=sid)
                    return

                task_id = await self.db.tasks.create(sid, node, data)

                if task_id > 0:
                    await self.socketio.emit("taskRequest", {'id': task_id, 'name': data['name'], 'data': data['data']},
                                       room=node['sid'])

                self.db.clients.quotas[sid]["jobs"].update(reserve_quota, task_id)
        except Exception as e:
            self.logger.error("Error in request {}: {}".format("skillRequest", data))
            self.logger.error(e)
            await self.socketio.emit("error", {"code": 500}, to=sid)

    async def results(self, sid, data):
        """
        Send results to client
        """
        try:
            if self.db.clients.quota(sid, append=True, is_result=True):
                await self.socketio.emit("error", {"code": 100}, to=sid)
                return

            if type(data) is dict and "id" in data and ("error" in data or "data" in data):
                await self.db.tasks.update(data["id"], sid, data)
            else:
                await self.socketio.emit("error", {"code": 111}, to=sid)
                return
        except Exception as e:
            self.logger.error("Error in request {}: {}".format("taskResults", data))
            self.logger.error("Error: {}".format(e))
            await self.socketio.emit("error", {"code": 500}, to=sid)

    async def abort(self, sid, data):
        """
        Send results to client
        """
        try:
            if self.db.clients.quota(sid, append=True):
                await self.socketio.emit("error", {"code": 100}, to=sid)
                return

            aborted = await self.db.tasks.abort_by_user(data["id"], sid)
            if not aborted:
                await self.socketio.emit("error", {"code": 106}, to=sid)
        except Exception as e:
            self.logger.error("Error in request {}: {}".format("requestAbort", data))
            self.logger.error(e)
            await self.socketio.emit("error", {"code": 500}, to=sid)
