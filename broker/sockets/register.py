from . import SocketRoute

from flask_socketio import emit
from flask import session

from celery import chain
from celery.result import AsyncResult

from celery_app import store_pdf, process_pdf

from db.registry import registry
from db.skill import Skill, NetNode

class RegisterRoute(SocketRoute):
    def __init__(self, path, socketio, celery):
        super().__init__(path, socketio, celery)

    def _init(self):
        self.socketio.on_event(f"register_skill", self.register)

    def register(self, data):
        sid = session["sid"]

        # currently we simply copy everything trusting the source
        skill = Skill(data["uid"], data["name"], data["config"])
        owner = NetNode(sid)

        registry.announce_skill(skill, owner)