import asyncio
import threading
import time
from datetime import datetime
from datetime import timedelta

from broker.db.collection import Collection
from broker.db.utils import results


class Tasks(Collection):
    """
    Task Collection

    @author: Dennis Zyska
    """

    def __init__(self, db, adb, config, socketio):
        super().__init__("tasks", db, adb, config, socketio)
        self.quotas = {}

        self.index = results(self.collection.add_hash_index(fields=['sid'], name='sid_index', unique=False))
        self.index = results(self.collection.add_hash_index(fields=['connected'], name='connected_index', unique=False))

        # start scrub task
        scrub_thread = threading.Thread(target=self.cron)
        scrub_thread.daemon = True
        scrub_thread.start()

    def create(self, sid, node, payload, parent=None):
        """
        Create a new task

        :param sid: sender id from request client
        :param node: node id send request to
        :param payload: task payload
        :param parent: parent task id
        :return:
        """
        # is max_runtime set?
        max_runtime = 0
        if "config" in payload and 'max_runtime' in payload['config']:
            max_runtime = payload['config']['max_runtime']
        if self.config['taskKiller']['enabled']:
            max_duration = self.config['taskKiller']['maxDuration']
            if max_runtime > max_duration:
                max_runtime = max_duration

        return results(self.collection.insert({
            "rid": sid,  # request id
            "nid": node,  # node id
            "request": payload,
            "status": "created",
            "parent": parent,
            "max_runtime": (datetime.now() + timedelta(
                seconds=max_runtime)).isoformat() if max_runtime > 0 else "9999-12-31T23:59:59.999Z",
            "start_timer": time.perf_counter(),
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
        }))

    def get(self, key):
        """
        Get task by key (sync)
        """
        return results(self.collection.get(key))

    def update(self, key, node, payload):
        """
        Update task by key

        :param key: key of task
        :param node: node the result came from
        :param payload: results of task
        """
        task = self.get(key)
        if 'status' in payload and payload['status'] != 'finished':
            last_update = task['updated']
            task['status'] = payload['status']
            task['updated'] = datetime.now().isoformat()
            task['updates'] = payload
            self.collection.update(task)

            if "config" in task['request'] and 'status' in task['request']['config']:
                last_update = datetime.fromisoformat(last_update)
                now = datetime.now()
                seconds = (now - last_update).total_seconds()
                if (task['request']['config'] < seconds):
                    # send status update to client
                    self.db.clients.quota(task['rid'], append=True)

                    output = {
                        'id': task['request']['id'],
                        'clientId': task['request']['clientId'] if 'clientId' in task['request'] else None,
                        'data': payload['data'] if isinstance(payload, dict) and 'data' in payload.keys() else {}
                    }
                    # sending status update to client if
                    self.socketio.emit("skillStatus", output, room=task['rid'])

        else:
            task['end_timer'] = time.perf_counter()
            task["duration"] = task['end_timer'] - task["start_timer"]
            task["result"] = payload
            task['status'] = 'finished'
            task["fid"] = node  # finish id
            self.collection.update(task)

            # update job quota
            self.db.clients.quotas[task['rid']]['jobs'].remove(task['_key'])

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
                        asyncio.sleep(
                            task['request']['config']['min_delay'] - (time.perf_counter() - task["start_timer"])))
                    tsk.add_done_callback(
                        lambda t: self.send_results(task['rid'], output))
                else:
                    asyncio.run(
                        asyncio.sleep(
                            task['request']['config']['min_delay'] - (time.perf_counter() - task["start_timer"])))
                    self.send_results(task['rid'], output)
            else:
                self.send_results(task['rid'], output)

            return {
                "rid": task["rid"],
                "output": output,
            }

    def cron(self):
        """
        Cronjob for cleaning up tasks
        """
        # TODO this function returns often an error
        # arango.exceptions.AQLQueryExecuteError: [HTTP 400][ERR 600] VPackError error: Expecting digit
        while self.config['taskKiller']['enabled']:
            cursor = results(self._sysdb.aql.execute("""
                FOR doc IN tasks
                FILTER doc.status == 'running' or doc.status == 'created'
                FILTER doc.max_runtime < DATE_NOW()
                RETURN doc
            """))
            for task in cursor:
                self.abort(task)
            time.sleep(self.config['taskKiller']['interval'])

    def terminate_by_disconnect(self, sid):
        """
        Abort all tasks because one client is disconnected
        :param sid: session id of user
        :return:
        """
        aql_query = """
                FOR doc IN @@collection
                FILTER (doc.status == "running" OR doc.status == "created")
                AND (doc.nid == @sid OR doc.rid == @sid)
                RETURN doc
            """
        cursor = results(self._sysdb.aql.execute(aql_query, bind_vars=
        {
            "@collection": self.name,
            "sid": sid
        }))
        for task in cursor:
            if task['nid'] == sid:
                # node disconnected, is there another node?
                node = self.db.skills.get_node(task['rid'], task['request']["name"])
                if node is None:
                    self.abort(task, reason="node disconnected", kill=False, error=103)
                else:
                    # start task on other node
                    task = self.db.tasks.create(task["rid"], node, task['request'], parent=task['_key'])
                    self.socketio.emit("taskRequest", {'id': task['_key'], 'data': task['request']['data']}, room=node)
                    self.abort(task, reason="node disconnected", kill=False, error=104)
            else:
                self.abort(task, reason="client disconnected", kill=True, error=False)

    def abort_by_user(self, id, sid):
        """
        Abort task by user
        :param id: task id
        :param sid: session id of user
        :return:
        """
        aql_query = """
                FOR doc IN @@collection
                FILTER (doc.status == "running" OR doc.status == "created")
                AND doc.rid == @rid
                AND doc.request.id == @id
                RETURN doc
                LIMIT 1
            """
        cursor = results(self._sysdb.aql.execute(aql_query, bind_vars=
        {
            "@collection": self.name,
            "rid": sid,
            "id": id
        }))
        if cursor.count() > 0:
            task = cursor.next()
            self.abort(task)
            return True
        return False

    def abort(self, task, reason="", kill=True, error=102):
        """
        Abort task by key
        :param task: task to abort
        :param reason: reason for abort
        :param kill: send kill emit to node
        :param error: send error code to client
        :return:
        """
        # send kill signal to node
        if kill:
            # TODO check if node accept kill feature
            self.socketio.emit("taskKill", {"id": task['_key']}, room=task['nid'])

        # update task
        task['status'] = "aborted"
        task['reason'] = reason
        task['updated'] = datetime.now().isoformat()
        self.collection.update(task)

        # update job quota
        self.db.clients.quotas[task['rid']]['jobs'].remove(task['_key'])

        # send results to client
        if error:
            self.socketio.emit("error", {"code": 102}, room=task['rid'])

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
        Clean up tasks on start
        """
        cleaned = results(self.collection.update_match({"connected": True}, {"connected": False, "cleaned": True}))
        self.logger.info("Cleaned up {} tasks".format(cleaned))

    def scrub(self, run_forever=True):
        """
        Regular task for cleaning db - delete old entries
        :param run_forever: run forever as called in thread
        :param max_age: overwrite max age threshold and force scrub
        :return:
        """
        once = True
        while run_forever or once:
            aql_query = """
                FOR doc IN tasks
                FILTER doc.status != 'running' && doc.status != 'created'
                FILTER doc.updated < @timestamp
                FILTER (NOT HAS(doc.request.config, 'donate') || doc.request.config.donate == false)
                RETURN doc
            """
            if self.config['scrub']['enabled'] and self.config['scrub']['maxAge'] > 0:
                timestamp_threshold = datetime.now() - timedelta(seconds=self.config['scrub']['maxAge'])
                query_params = {'timestamp': timestamp_threshold.isoformat()}
                cursor = results(self._sysdb.aql.execute(aql_query, bind_vars=query_params))
                for entry in cursor:
                    print("Delete by scrub: Task {}".format(entry['_key']))
                    self.collection.delete(entry['_key'])
            if run_forever:
                time.sleep(self.config['scrub']['interval'])
            once = False
