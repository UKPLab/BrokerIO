from typing import List
from datetime import datetime as Timestamp


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

    def _parse_config(self, config):
        #todo
        self.input = "implement _parse_config first"
        self.output = "implement _parse_config first"
        self.requires = ["implement _parse_config first"]


class NetNode:
    """
    Represents a network node announcing its skills.
    """
    session_id: str = None

    def __init__(self, session_id):
        self.session_id = session_id


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