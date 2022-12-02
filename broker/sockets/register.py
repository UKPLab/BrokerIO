import json

from . import SocketRoute

from flask_socketio import emit
from flask import session

from celery import chain
from celery.result import AsyncResult

from celery_app import request_skill_by_uid

from db.registry import registry
from db.skill import Skill, NetNode


class RegisterRoute(SocketRoute):
    def __init__(self, name, socketio, celery):
        super().__init__(name, socketio, celery)

    def _init(self):
        self.socketio.on_event("register_skill", self.register)
        self.socketio.on_event("get_info", self.inform)
        self.socketio.on_event("request_skill", self.request)

    def register(self, data):
        sid = session["sid"]

        # currently we simply copy everything trusting the source
        skill = Skill(data["name"], data)
        owner = NetNode(sid)

        registry.announce_skill(skill, owner)

    def inform(self):
        #todo could get quite large, if we transfer the whole config on inform call...

        announcements = registry.get_entries()
        self.socketio.emit("info", json.dumps([a.to_dict() for a in announcements]), room=session["sid"])

    def request(self, data):
        sid = session["sid"]

        #todo distribute to suitable method depending on the data payload (for now: default by uid)

        # get skill request information
        request_skill_by_uid.delay(sid, data)