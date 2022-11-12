from . import SocketRoute

from flask_socketio import emit
from flask import session

from celery import chain
from celery.result import AsyncResult

from celery_app import store_pdf, process_pdf

from db.registry import registry
from db.skill import Skill, NetNode


class RegisterRoute(SocketRoute):
    def __init__(self, name, socketio, celery):
        super().__init__(name, socketio, celery)

    def _init(self):
        self.socketio.on_event("register_skill", self.register)
        self.socketio.on_event("get_info", self.inform)

    def register(self, data):
        sid = session["sid"]

        # currently we simply copy everything trusting the source
        skill = Skill(data["uid"], data["name"], data["config"])
        owner = NetNode(sid)

        registry.announce_skill(skill, owner)

    def inform(self):
        announcements = registry.get_entries(as_json=True)
        self.socketio.emit("info", announcements, room=session["sid"])
