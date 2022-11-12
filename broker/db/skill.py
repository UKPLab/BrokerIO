import io
import json
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

    input: str = None
    output: str = None
    requires: List = None

    def __init__(self, uid, name, config):
        self.uid = uid
        self.name = name

        self._parse_config(config)

    def _parse_config(self, config: str):
        # parse yaml (savely)
        with io.StringIO(config) as f:
            config = yaml.safe_load(f)

        # config can be none at this point

        # populate attributes from config dict
        self.input = "implement _parse_config first"
        self.output = "implement _parse_config first"
        self.requires = ["implement _parse_config first"]

    def to_dict(self):
        return self.__dict__


class NetNode:
    """
    Represents a network node announcing its skills.
    """
    session_id: str = None

    def __init__(self, session_id):
        self.session_id = session_id

    def to_dict(self):
        return self.__dict__


class Announcement:
    """
    Represents the announcement of a skill as provided by model nodes.
    """
    uid: str = None
    created_at:  Timestamp = None
    updated_at: Timestamp = None

    skill: Skill = None
    owner: NetNode = None

    def __init__(self, uid, skill, owner):
        self.uid = uid
        self.skill = skill
        self.owner = owner

        self.created_at = Timestamp.now()
        self.updated_at = Timestamp.now()

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