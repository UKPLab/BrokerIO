import asyncio
import os
import threading
import time
from datetime import datetime, timedelta

from broker import init_logging
from broker.db import results


class Tasks:
    """
    Representation of a task in the broker

    @author: Dennis Zyska
    """

    def __init__(self, db, socketio):
        self.socketio = socketio
        self.logger = init_logging("tasks")
        self._db = db
        if results(db.has_collection("tasks")):
            self.db = db.collection("tasks")
        else:
            self.db = results(db.create_collection("tasks"))

        self.scrub_max_age = int(os.getenv("SCRUB_MAX_AGE", 3600))
        self.scrub_interval = int(os.getenv("SCRUB_INTERVAL", 3600))
        self.clean()

        # start scrub task
        scrub_thread = threading.Thread(target=self.scrub)
        scrub_thread.daemon = True
        scrub_thread.start()

    def create(self, sid, node, payload):
        """
        Create a new task

        :param sid: sender id from request client
        :param node: node id send request to
        :param payload: task payload
        :return:
        """
        return results(self.db.insert({
            "rid": sid,  # request id
            "nid": node,  # node id
            "request": payload,
            "start_timer": time.perf_counter(),
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
        }))

    def get(self, key):
        """
        Get task by key (sync)
        """
        return results(self.db.get(key))

    def finish(self, key, node, payload):
        """
        Update task by key

        :param key: key of task
        :param node: node the result came from
        :param payload: results of task
        """
        task = self.get(key)
        task['end_timer'] = time.perf_counter()
        task["duration"] = task['end_timer'] - task["start_timer"]
        task["result"] = payload
        task["fid"] = node  # finish id
        self.db.update(task)

        output = {
            'id': task['request']['id'],
            'clientId': task['request']['clientId'] if 'clientId' in task['request'] else None,
            'data': payload['data'] if isinstance(payload, dict) and 'data' in payload.keys() else {}
        }
        if "config" in task['request'] and 'return_stats' in task['request']['config']:
            output['stats'] = {
                'duration': task["duration"],
                'host': node,
            }
        if "config" in task['request'] and 'min_delay' in task['request']['config']:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:  # 'RuntimeError: There is no current event loop...'
                loop = None

            if loop and loop.is_running():
                # https://docs.python.org/3/library/asyncio-task.html#task-object
                tsk = loop.create_task(
                    asyncio.sleep(task['request']['config']['min_delay'] - (time.perf_counter() - task["start_timer"])))
                tsk.add_done_callback(
                    lambda t: self.send_results(task['rid'], output))
            else:
                asyncio.run(
                    asyncio.sleep(task['request']['config']['min_delay'] - (time.perf_counter() - task["start_timer"])))
                self.send_results(task['rid'], output)
        else:
            self.send_results(task['rid'], output)

        return {
            "rid": task["rid"],
            "output": output,
        }

    def send_results(self, rid, payload):
        """
        Send results to request client
        :param rid: session id of request client
        :param payload: data to send
        :return:
        """
        self.socketio.emit("skillResults", payload, room=rid)

    def clean(self):
        """
        Clean up tasks
        """
        cleaned = results(self.db.update_match({"connected": True}, {"connected": False, "cleaned": True}))
        self.logger.info("Cleaned up {} tasks".format(cleaned))

    def scrub(self):
        """
        Regular task for cleaning db - delete old entries
        :return:
        """
        while True:
            aql_query = """
                FOR doc IN tasks
                FILTER doc.updated < @timestamp
                RETURN doc
            """
            if self.scrub_max_age > 0:
                timestamp_threshold = datetime.now() - timedelta(seconds=self.scrub_max_age)
                query_params = {'timestamp': timestamp_threshold.isoformat()}
                cursor = results(self._db.aql.execute(aql_query, bind_vars=query_params))
                for entry in cursor:
                    print("Delete by scrub: Task {}".format(entry['_key']))
                    self.db.delete(entry['_key'])
            time.sleep(self.scrub_interval)
