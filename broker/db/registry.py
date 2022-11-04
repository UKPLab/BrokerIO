from typing import List

from db.skill import Announcement, Skill, NetNode

from uuid import uuid4


class Registry:
    """
    Represents the database of registered skills. In the future this class object will be replaced
    by a database interface.
    """
    rows: List[Announcement] = None

    def __init__(self):
        self.rows = []

    def connect(self):
        # dummy method
        print("Connected to registry")

    def announce_skill(self, skill: Skill, owner: NetNode):
        print(f"Registered a new skill: {skill.uid} ({skill.name}) by {owner.session_id}")
        self.rows.append(Announcement(uuid4(), skill, owner))

    def un_announce_skill(self, announcement_id: str):
        try:
            i,a = next((i, a) for i, a in enumerate(self.rows) if a.uid == announcement_id)
        except StopIteration:
            raise ValueError(f"Passed announcement {announcement_id} is not registered. Failed to un-announce.")

        print(f"Unteregistered a skill: {a.skill.uid} ({a.skill.name}) by {a.owner.session_id}")
        del self.rows[i]
        return a


registry = Registry()
