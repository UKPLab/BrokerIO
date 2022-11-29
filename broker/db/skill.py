import io
import json
import time
from typing import List
from datetime import datetime as Timestamp

import yaml


class Skill:
    """
    Represents a skill, which will be stored in the registry. Later on this class will be loaded and written
    to an actual database. They are encapusled within an announcement
    """
    uid: str = None
    name: str = None

    config_yaml: str = None
    _parsed_config: dict = None

    def __init__(self, uid, name, config):
        self.uid = uid
        self.name = name
        self.config_yaml = config

    @property
    def config(self):
        if self._parsed_config is None:
            self._parse_config()

        return self._parsed_config

    def _parse_config(self):
        if self.config is None:
            return

        # parse yaml (savely)
        with io.StringIO(self.config) as f:
            config = yaml.safe_load(f)

        # config can be none at this point
        self._parsed_config = config

    def to_dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "config": self.config_yaml
        }

    @staticmethod
    def from_dict(data):
        return Skill(data["uid"], data["name"], data["config"])


class NetNode:
    """
    Represents a network node announcing its skills.
    """
    session_id: str = None

    def __init__(self, session_id):
        self.session_id = session_id

    def to_dict(self):
        return {
            "session_id": self.session_id
        }

    @staticmethod
    def from_dict(data):
        return NetNode(data["session_id"])


class Announcement:
    """
    Represents the announcement of a skill as provided by model nodes.
    """
    uid: str = None
    created_at: Timestamp = None
    updated_at: Timestamp = None

    skill: Skill = None
    owner: NetNode = None

    def __init__(self, uid, skill, owner, created_at=None, updated_at=None):
        self.uid = uid
        self.skill = skill
        self.owner = owner

        self.created_at = Timestamp.now() if created_at is None else created_at
        self.updated_at = Timestamp.now() if updated_at is None else updated_at

    def __eq__(self, other):
        return self.uid == other.uid

    def to_dict(self):
        return {
            "uid": self.uid,
            "created_at": self.created_at.strftime("%Y/%m/%dT%H:%M:%S%Z"),
            "updated_at": self.created_at.strftime("%Y/%m/%dT%H:%M:%S%Z"),
            "skill": self.skill.to_dict(),
            "owner": self.owner.to_dict()
        }

    @staticmethod
    def from_dict(data):
        skill = Skill.from_dict(data["skill"])
        owner = NetNode.from_dict(data["owner"])

        return Announcement(data["uid"],
                            skill=skill,
                            owner=owner,
                            created_at=time.strptime(data["created_at"], "%Y/%m/%dT%H:%M:%S%Z"),
                            updated_at=time.strptime(data["updated_at"], "%Y/%m/%dT%H:%M:%S%Z"))
