import random
from datetime import datetime
from uuid import uuid4


class Skills:
    """
    Represents skills from the database

    @author: Dennis Zyska
    """

    def __init__(self, db, socketio):
        self.socketio = socketio

        if db.has_collection("skills").result():
            self.db = db.collection("skills")
        else:
            self.db = db.create_collection("skills").result()

        self.index = self.db.add_hash_index(fields=['sid'], name='sid_index', unique=False).result()
        self.index = self.db.add_hash_index(fields=['connected'], name='connected_index', unique=False).result()

        self.clean()

    def register(self, sid, data):
        """
        Register a new skill

        :param sid: session id of skill node
        :param data: skill data
        """
        self.db.insert(
            {
                "uid": str(uuid4()),
                "sid": sid,
                "config": data,
                "connected": True,
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "last_contact": datetime.now().isoformat(),
                "first_contact": datetime.now().isoformat(),
                "reconnects": 1,
            }
        ).result()
        self.send_update(data["name"])

    def unregister(self, sid):
        """
        Unregister a skill

        :param sid: session id of skill node
        """
        skills = self.db.find({"sid": sid, "connected": True}).result()
        if len(skills) > 0:
            skill = skills.next()
            skill["connected"] = False
            skill["last_contact"] = datetime.now().isoformat()
            self.db.update(skill).result()
            self.send_update(skill["config"]["name"])

    def send_update(self, name=None, with_config=False, **kwargs):
        """
        Send update to all connected clients

        If name is given, only send update for this skill

        :param name: name of skill
        :param with_config: send with config
        :param kwargs: additional arguments for socketio.emit
        """
        if name:
            self.socketio.emit("skillUpdate", [self.get_skill(name, with_config=with_config)], **kwargs)
        else:
            all_skills = self.get_skills(with_config=with_config)
            self.socketio.emit("skillUpdate", [all_skills[key] for key in all_skills.keys()], **kwargs)

    def get_node(self, name):
        """
        Get a random node by name

        :param name: Skill name
        :return: random node id (session id)
        """
        skills = self.db.find({"config.name": name, "connected": True}).result()
        if len(skills) == 0:
            return None

        pos = random.randint(0, len(skills) - 1)
        for i in range(0, pos):
            skill = skills.next()
        return skills.next()["sid"]

    def get_skill(self, name, with_config=False):
        """
        Get a skill by name (aggregated, only first config is used)

        :param name: Skill name
        :param with_config: with config
        """
        skills = self.db.find({"config.name": name, "connected": True}).result()
        if len(skills) == 0:
            return {
                "nodes": 0,
                "name": name,
            }

        skill = skills.next()
        data = {
            "nodes": len(skills),
            "name": skill["config"]["name"],
        }
        if with_config:
            data["config"] = skill["config"]
        return data

    def get_skills(self, with_config=False):
        """
        Get list of skills (aggregated)

        :param with_config: with config
        """
        skills = self.db.find({"connected": True}).result()
        skill_list = {}
        for skill in skills:
            name = skill["config"]["name"]
            if name not in skill_list:
                skill_list[name] = {
                    "nodes": 1,
                    "name": name,
                }
                if with_config:
                    skill_list[name]["config"] = skill["config"]
            else:
                skill_list[name]["nodes"] += 1
        return skill_list

    def clean(self):
        """
        Clean up database
        """
        self.db.update_match({"connected": True}, {"connected": False, "cleaned": True})
