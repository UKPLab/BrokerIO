from datetime import datetime

from flask_socketio import join_room

from broker import init_logging
from broker.db import results
from broker.utils.Quota import Quota


class Clients:
    """
    Representation of a client in the broker (through db)

    @author: Dennis Zyska
    """

    def __init__(self, db, config, socketio):
        self.socketio = socketio
        self.config = config
        self.quotas = {}

        self.logger = init_logging("clients")

        if results(db.has_collection("clients")):
            self.db = db.collection("clients")
        else:
            self.db = results(db.create_collection("clients"))
        self.index = results(self.db.add_hash_index(fields=['sid'], name='sid_index', unique=False))

        self.clean()

    def connect(self, sid, ip, data):
        """
        Connect a client
        :param sid: session id
        :param ip: ip address
        :param data: payload
        :return:
        """
        join_room(sid)
        user = results(self.db.insert(
            {
                "sid": sid,
                "ip": ip,
                "data": data,
                "connected": True,
                "first_contact": datetime.now().isoformat(),
                "last_contact": datetime.now().isoformat(),
            }
        ))

        # add quota for sid
        self._apply_quota(sid, "guest")

        return user

    def disconnect(self, sid):
        self.db.update_match({"sid": sid, "connected": True},
                             {'last_contact': datetime.now().isoformat(), 'connected': False})

        # remove sid from quota
        del self.quotas[sid]

        # close room
        self.socketio.close_room(sid)

        # cancel jobs
        # TODO cancel open jobs

    def _apply_quota(self, sid, role):
        """
        Set quota for client
        :param sid: session id
        :param role: name of the role
        :return:
        """
        if sid in self.quotas:
            del self.quotas[sid]

        self.quotas[sid] = {
            "role": role,
            "requests": Quota(max_len=int(self.config['quota'][role]['requests']) + 1),
            "results": Quota(max_len=int(self.config['quota'][role]['results']) + 1),
        }

    def get(self, sid):
        """
        Get client by sid
        :param sid: session id
        :return:
        """
        client = results(self.db.find({"sid": sid, "connected": True}))
        if client.count() > 0:
            return client.next()

    def register(self, sid, secret):
        """
        Try to register a client with a public key
        :param secret: secret string
        :param sid: session id
        :return:
        """
        self.db.update_match({"sid": sid, "connected": True},
                             {'last_contact': datetime.now().isoformat(), 'secret': secret})

    def save(self, client):
        """
        Save a client object
        :param client: client object
        :return:
        """
        # update quota if role changed
        if "role" in client:
            if self.quotas[client["sid"]]["role"] != client["role"]:
                self._apply_quota(client["sid"], client["role"])

        self.db.update(client)

    def check_quota(self, sid, append=False, is_result=False):
        """
        Check if a client is allowed to send data
        :param is_result: use results quota
        :param sid: session id
        :param append: append to quota
        :return: True if quota is exceeded
        """
        self.db.update_match({"sid": sid, "connected": True}, {'last_contact': datetime.now().isoformat()})
        if is_result:
            return self.quotas[sid]['results'](append)
        return self.quotas[sid]['requests'](append)

    def clean(self):
        """
        Clean up old clients and reset quota
        """
        cleaned = results(self.db.update_match({"connected": True}, {"connected": False, "cleaned": True}))
        self.logger.info("Cleaned up {} clients".format(cleaned))
