import random
from datetime import datetime
from uuid import uuid4

from broker.db import results
from broker.db.collection import Collection


class Skills(Collection):
    """
    Skill Collection

    @author: Dennis Zyska
    """

    def __init__(self, db, adb, config, socketio):
        super().__init__("skills", db, adb, config, socketio)
        self.quotas = {}

        self.index = results(self.collection.add_hash_index(fields=['sid'], name='sid_index', unique=False))
        self.index = results(self.collection.add_hash_index(fields=['connected'], name='connected_index', unique=False))

    def register(self, sid, data):
        """
        Register a new skill

        :param sid: session id of skill node
        :param data: skill data
        """
        results(self.collection.insert(
            {
                "uid": str(uuid4()),
                "sid": sid,
                "config": data,
                "connected": True,
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "last_contact": datetime.now().isoformat(),
                "first_contact": datetime.now().isoformat(),
            }
        ))
        self.send_update(data["name"])

    def unregister(self, sid):
        """
        Unregister a skill

        :param sid: session id of skill node
        """
        skills = results(self.collection.find({"sid": sid, "connected": True}))
        if len(skills) > 0:
            skill = skills.next()
            skill["connected"] = False
            skill["last_contact"] = datetime.now().isoformat()
            results(self.collection.update(skill))
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
            skill = self.get_skill(name, with_config=with_config)
            print(skill)
            exit()
            if 'roles' in skill['config']:
                for role in skill['config']['roles']:
                    self.socketio.emit("skillUpdate", [skill], room="role:{}".format(role), **kwargs)
            else:
                self.socketio.emit("skillUpdate", [skill], **kwargs)
        else:
            all_skills = self.get_skills(with_config=with_config)

            if len(all_skills) == 0:
                return

            # TODO check skill are only send to the users with the right role
            print("All Skills", all_skills)

            all_skills = [all_skills[key] for key in all_skills.keys()]

            # distribute to roles
            skills_admin = []
            skills_user = []
            skills_guest = []

            print(all_skills)
            exit()

            for skill in all_skills:
                if 'role' in skill['config']:
                    for role in skill['config']['roles']:
                        if role == 'admin':
                            skills_admin.append(skill)
                        elif role == 'user':
                            skills_user.append(skill)
                        elif role == 'guest':
                            skills_guest.append(skill)
                else:
                    skills_guest.append(skill)

            if len(skills_admin) > 0:
                self.socketio.emit("skillUpdate", skills_admin, room="role:admin", **kwargs)

            if len(skills_user) > 0:
                self.socketio.emit("skillUpdate", skills_user, room="role:user", **kwargs)

            if len(skills_guest) > 0:
                self.socketio.emit("skillUpdate", skills_guest, room="role:guest", **kwargs)

    def get_node(self, name):
        """
        Get a random node by name

        :param name: Skill name
        :return: random node id (session id)
        """
        skills = results(self.collection.find({"config.name": name, "connected": True}))
        if len(skills) == 0:
            return None

        # TODO check if the user can use this skill!

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
        skills = results(self.collection.find({"config.name": name, "connected": True}))
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
        skills = results(self.collection.find({"connected": True}))
        return [{
            "name": skill["config"]["name"],
            "nodes": 1,
        }
            for skill in skills
        ]

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
        cleaned = results(self.collection.update_match({"connected": True}, {"connected": False, "cleaned": True}))
        self.logger.info("Cleaned up {} skills".format(cleaned))
