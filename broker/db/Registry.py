import json
from typing import List
from uuid import uuid4

import redis

from broker.db.Announcement import Announcement, Skill, NetNode


class Registry:
    """
    Represents the database of registered skills. In the future this class object will be replaced
    by a database interface.
    """
    rows: List[Announcement] = None

    def __init__(self, redis_host, redis_port):
        self.redis = None
        self.rows = []
        self.registered_nodes = {}

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
        print(f"Registered a new skill: {skill.config['name']} by {owner.session_id}")

        a = Announcement(str(uuid4()), skill, owner)

        self.registered_nodes[owner.session_id] = a.uid

        self.redis.append(a.uid, json.dumps(a.to_dict()))

    def un_announce_skill(self, announcement_id: str):
        # todo error handling
        a = self.redis.getdel(announcement_id)
        a = json.loads(a.decode('utf-8'))
        print(a)

        print(f"Unregistered a skill: {a['skill']['name']} by {a['owner']['session_id']}")

        return a

    def get_entries(self, skill_only=False):
        aa = self.redis.keys()

        print("redis keys", aa)

        if skill_only:
            return [self.get_entry(a)['skill'] for a in aa]
        else:
            return [self.get_entry(a) for a in aa]

    def get_skills(self, with_config=True):
        """
        Get list of skills (aggregated)
        """
        aa = self.get_entries(True)
        skills = {}
        for a in aa:
            if a['name'] not in skills:  # only first config is used
                skills[a['name']] = a if with_config else {'name': a['name']}
                skills[a['name']]['nodes'] = 1
            else:
                skills[a['name']]['nodes'] += 1
        return skills

    def get_skill(self, name, with_config=True):
        """
        Get config of an explicit skill by name
        """
        skills = self.get_skills(with_config=with_config)
        if name in skills:
            return self.get_skills(with_config=with_config)[name]
        else:
            return {'name': name, 'nodes': 0}

    def get_entry(self, uid):
        # todo error handling
        a_data = self.redis.get(uid)

        return json.loads(a_data)

    def remove_owner(self, sid):
        """
        Remove owner by sid

        Returns None if not registered!

        @return announcement object
        """
        if sid in self.registered_nodes:
            return self.un_announce_skill(self.registered_nodes[sid])
