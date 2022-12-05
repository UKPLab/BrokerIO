import json
import os

import redis
from typing import List

from broker.db.skill import Announcement, Skill, NetNode

from uuid import uuid4

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")


class Registry:
    """
    Represents the database of registered skills. In the future this class object will be replaced
    by a database interface.
    """
    rows: List[Announcement] = None

    def __init__(self, redis_host, redis_port):
        self.rows = []

        self.host = redis_host
        self.port = redis_port

    def connect(self):
        print(f"Connecting to redis at {self.host}:{self.port}...")

        self.redis = redis.Redis(host=self.host, port=self.port)
        res = self.redis.ping()

        assert res, "Failed to connect to REDIS backend. Cannot start registry"

        print(f"Redis connection established: {res}")

    def clean(self):
        print("Cleaning redis store...")

        cnt = 0
        for key in self.redis.scan_iter():
            self.redis.delete(key)
            cnt += 1

        print(f"Discarded {cnt} entries from reddis on initialization")

    def announce_skill(self, skill: Skill, owner: NetNode):
        print(f"Registered a new skill: {skill.uid} ({skill.name}) by {owner.session_id}")

        a = Announcement(str(uuid4()), skill, owner)
        self.redis.append(a.uid, json.dumps(a.to_dict()))

    def un_announce_skill(self, announcement_id: str):
        # todo error handling
        a = self.redis.getdel(announcement_id)

        print(f"Unteregistered a skill: {a.skill.uid} ({a.skill.name}) by {a.owner.session_id}")

        return a

    def get_entries(self):
        aa = self.redis.keys()

        print("redis keys", aa)

        return [self.get_entry(a) for a in aa]

    def get_entry(self, uid):
        #todo error handling
        a_data = self.redis.get(uid)

        return Announcement.from_dict(json.loads(a_data))


registry = Registry(REDIS_HOST, REDIS_PORT)