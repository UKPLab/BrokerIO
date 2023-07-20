from datetime import datetime

from broker.db.collection import Collection
from broker.db.utils import results


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
        skills = self.get_skills(filter_name=data['name'], with_config=True)
        if len(skills) > 0:
            if not skills[0]['config'] == data['config']:
                self.socketio.emit("error", {"code": 201}, to=sid)

        skill = {
            "sid": sid,
            "config": data,
            "connected": True,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "last_contact": datetime.now().isoformat(),
            "first_contact": datetime.now().isoformat(),
        }

        results(self.collection.insert(
            skill
        ))
        self.send_update(skill, len(skills) + 1)

    def unregister(self, sid):
        """
        Unregister all skills from a node

        :param sid: session id of skill node
        """
        skills = results(self.collection.find({"sid": sid, "connected": True}))
        for skill in skills:
            # send update first
            skills = self.get_skills(filter_name=skill['config']['name'], with_config=True)
            self.send_update(skill, len(skills) - 1)

            skill["connected"] = False
            skill["last_contact"] = datetime.now().isoformat()
            results(self.collection.update(skill))

    def send_update(self, skill, nodes, **kwargs):
        """
        Send update to all connected clients

        If name is given, only send update for this skill

        :param nodes: number of nodes available for this skill
        :param skill: skill data entry from db
        :param with_config: send with config
        :param kwargs: additional arguments for socketio.emit
        """
        self.logger.error(skill)
        if 'roles' in skill['config']:
            for role in skill['config']['roles']:
                self.socketio.emit("skillUpdate", [{"name": skill['config']['name'], "nodes": nodes}],
                                   room="role:{}".format(role), **kwargs)
        else:
            self.socketio.emit("skillUpdate", [{"name": skill['config']['name'], "nodes": nodes}], **kwargs)

    def send_all(self, role, with_config=False, **kwargs):
        """
        Send update to all connected clients
        :param with_config:
        :param role: filter skills for role
        :param kwargs:
        :return:
        """
        all_skills = self.get_skills(filter_role=role, with_config=with_config)

        if all_skills:
            self.socketio.emit("skillUpdate", all_skills, **kwargs)

    def get_node(self, sid, name):
        """
        Get a random node by name

        :param name: Skill name
        :param sid: session id of the requested user
        :return: random node id (session id)
        """
        user = self.db.clients.get(sid)
        aql_query = """
                FOR doc IN @@collection
                FILTER doc.connected 
                FILTER (!HAS("roles", doc.config) or @role IN doc.config.roles)
                SORT RAND()
                LIMIT 1
                RETURN doc
            """
        cursor = results(
            self._sysdb.aql.execute(aql_query, bind_vars={"@collection": self.name, "role": user["role"]}, count=True))

        if cursor.count() > 0:
            return cursor.next()["sid"]

    def get_skill(self, name):
        """
        Get a skill by name (aggregated, only first config is used)

        :param name: Skill name
        """
        return results(self.collection.find({"config.name": name, "connected": True}, limit=1))

    def get_skills(self, filter_name=None, filter_role=None, with_config=False):
        """
        Get list of skills (aggregated)

        :param with_config: with config
        :param filter_name: filter by name
        :param filter_role: filter by role
        :return: list of skills
        """
        skills = []

        filtering = {
            "filter_name": "FILTER doc.config.name == @name" if filter_name is not None else "",
            "filter_role": "FILTER (!HAS('roles', doc.config) or @role IN doc.config.roles)" if filter_role is not None else "",
            "return": "RETURN { name: name, nodes: nodes }"
        }
        aql_query = """
            FOR doc IN @@collection
            FILTER doc.connected 
            {filter_name}
            {filter_role}
            COLLECT name = doc.config.name, node = doc.config.name WITH COUNT INTO nodes
            {return}
        """.format(**filtering)
        bind_vars = {"@collection": self.name}
        if filter_name is not None:
            bind_vars["name"] = filter_name
        if filter_role is not None:
            bind_vars["role"] = filter_role
        cursor = results(self._sysdb.aql.execute(aql_query, bind_vars=bind_vars, count=True))
        for skill in cursor:
            if with_config:
                skill_config = results(
                    self.collection.find({"config.name": skill["name"], "connected": True}, limit=1))
                if skill_config.has_more():
                    skill["config"] = skill_config.next()["config"]
            skills.append(skill)
        return skills

    def clean(self):
        """
        Clean up database
        """
        cleaned = results(self.collection.update_match({"connected": True}, {"connected": False, "cleaned": True}))
        self.logger.info("Cleaned up {} skills".format(cleaned))
