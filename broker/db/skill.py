import time
import uuid
from datetime import datetime


class Skill:
    """
    Represents a skill, which will be stored in the registry. Later on this class will be loaded and written
    to an actual database. They are encapusled within an announcement
    """
    uid: str = None
    name: str = None

    config: dict = None

    def __init__(self, name, config):
        self.uid = str(uuid.uuid4())
        self.name = name
        self.config = config

    def to_dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "config": self.config
        }

    @staticmethod
    def from_dict(data):
        return Skill(data["name"], data)


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
    created_at: datetime = None
    updated_at: datetime = None

    skill: Skill = None
    owner: NetNode = None

    def __init__(self, uid, skill, owner, created_at=None, updated_at=None):
        self.uid = uid
        self.skill = skill
        self.owner = owner

        self.created_at = datetime.now() if created_at is None else created_at
        self.updated_at = datetime.now() if updated_at is None else updated_at

    def __eq__(self, other):
        return self.uid == other.uid

    def to_dict(self):
        return {
            "uid": self.uid,
            "created_at": datetime.strftime(self.created_at, "%Y/%m/%dT%H:%M:%S"),
            "updated_at": datetime.strftime(self.created_at, "%Y/%m/%dT%H:%M:%S"),
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
                            created_at=datetime.strptime(data["created_at"], "%Y/%m/%dT%H:%M:%S"),
                            updated_at=datetime.strptime(data["updated_at"], "%Y/%m/%dT%H:%M:%S"))
