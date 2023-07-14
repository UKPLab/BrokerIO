from datetime import datetime

from broker.db import results
from broker.db.collection import Collection
from broker.utils.Keys import Keys


class Users(Collection):
    """
    Users Collection

    @author: Dennis Zyska
    """

    def __init__(self, db, adb, config, socketio):
        super().__init__("users", db, adb, config, socketio)
        self.quotas = {}

        self.index = results(self.collection.add_hash_index(fields=['sid'], name='sid_index', unique=False))
        self.index = results(self.collection.add_hash_index(fields=['connected'], name='connected_index', unique=False))

    def _init(self, reinit=False):
        """
        Check if necessary keys exists, if not create
        :param reinit: overwrite basic clients
        :return:
        """
        super()._init()

        basic_client = results(self.collection.find({"system": True}))
        if reinit or basic_client.count() == 0:

            # load keys
            keys = Keys(private_key_path="./private_key.pem")
            if basic_client.count() > 0:
                for c in basic_client:
                    if basic_client.has_more():
                        self.collection.delete(c)

                c['key'] = keys.get_public()
                c['updated'] = datetime.now().isoformat()

                results(self.collection.update(c))

            else:
                # generate key pair
                results(self.collection.insert(
                    {
                        "system": True,
                        "role": "admin",
                        "authenticated": 0,
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
        client = results(self.collection.find({"key": public}))
        if client.count() > 0:
            c = client.next()
            c['authenticated'] = c['authenticated'] + 1
            c["updated"]: datetime.now().isoformat()
            return results(self.collection.update(c))
        else:
            return results(self.collection.insert(
                {
                    "role": "user",
                    "key": public,
                    "authenticated": 1,
                    "created": datetime.now().isoformat(),
                    "updated": datetime.now().isoformat()
                }
            ))

    def get(self, key):
        """
        Get user by key
        :param key: key
        :return:
        """
        return results(self.collection.get(key))
