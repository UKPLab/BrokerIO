from datetime import datetime

from broker import init_logging
from broker.db import results
from broker.utils.Keys import Keys
import uuid

class Users:
    """
    Representation of a client in the broker (through db)

    @author: Dennis Zyska
    """

    def __init__(self, db, socketio):
        self.socketio = socketio
        self.logger = init_logging("users")

        if results(db.has_collection("users")):
            self.db = db.collection("users")
        else:
            self.db = results(db.create_collection("users"))
        self.index = results(self.db.add_hash_index(fields=['username'], name='username_index', unique=False))

        self.init()

    def init(self, reinit=False):
        """
        Check if necessary keys exists, if not create
        :param reinit: overwrite basic clients
        :return:
        """
        basic_client = results(self.db.find({"system": True}))
        if reinit or basic_client.count() == 0:

            # load keys
            keys = Keys(private_key_path="./private_key.pem")
            if basic_client.count() > 0:
                for c in basic_client:
                    if basic_client.has_more():
                        self.db.delete(c)

                c['key'] = keys.get_public()
                c['updated'] = datetime.now().isoformat()

                results(self.db.update(c))

            else:
                # generate key pair
                results(self.db.insert(
                    {
                        "system": True,
                        "role": "admin",
                        "key": keys.get_public(),
                        "created": datetime.now().isoformat(),
                        "updated": datetime.now().isoformat()
                    }
                ))

    def auth(self, public):
        """
        Register user
        :param data: public key and additional infos
        :return:
        """
        # make sure the public key doesn't exists
        client = results(self.db.find({"public": public}))
        if client.count() > 0:
            c = client.next()
            c['authenticated'] += 1
            c["updated"]: datetime.now().isoformat()
            return results(self.db.update(c))
        else:
            # generate key pair
            return results(self.db.insert(
                {
                    "role": "default",
                    "key": public,
                    "authenticated": 1,
                    "created": datetime.now().isoformat(),
                    "updated": datetime.now().isoformat()
                }
            ))
