""" Skill for PD3F PDF text extraction

This skill is a simple skill that uses the PD3F PDF text extraction tool to extract text from a PDF file.

https://github.com/pd3f/pd3f
https://pd3f.github.io/pd3f-core/export.html#pd3f.export.extract

Author: Dennis Zyska
"""

import base64
import logging
import multiprocessing as mp
import multiprocessing.queues as mpq
import os
import sys
import time
from multiprocessing import Process, Queue

from pd3f import extract

from brokerio.skills.templates.simpleSkill.LoggingJsonFormatter import LoggingJsonFormatter
from brokerio.skills.templates.simpleSkill.Skill import Skill as SkillSimple

logging.basicConfig(level=logging.INFO)


# This is a Queue that behaves like stdout
class StdoutQueue(mpq.Queue):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, ctx=mp.get_context())

    def write(self, msg):
        self.put(msg)

    def flush(self):
        sys.__stdout__.flush()


def run_parsr(log_queue, output_queue, parsr_localtion, pdf_file, params):
    # move std output to log queue
    # sys.stdout = log_queue

    logger = logging.getLogger('pd3f')
    queue_handler = logging.handlers.QueueHandler(log_queue)
    queue_handler.setFormatter(LoggingJsonFormatter({"level": "levelname",
                                                     "message": "message",
                                                     "loggerName": "name",
                                                     "processName": "processName",
                                                     "processID": "process",
                                                     "threadName": "threadName",
                                                     "threadID": "thread",
                                                     "timestamp": "asctime"}))
    logger.addHandler(queue_handler)
    logger.setLevel(logging.INFO)

    # run parsr
    text, tables = extract(pdf_file, parsr_location=parsr_localtion, **params)

    # put results into output queue
    output_queue.put((text, tables))


class Skill(SkillSimple):
    """
    Skill for OpenAI API
    """

    def __init__(self):
        super().__init__()
        self.description = "This is a pdf text extraction skill based on pd3f"
        self.tmp_file = "/app/pd3f.pdf"
        self.parsr_location = "{}_{}:3001".format(os.environ.get("CONTAINER_NAME"), 'parsr')
        self.p = None
        self.features = ['status']

    def init(self):
        """
        Initialize Open AI Connection
        :return:
        """
        pass

    def execute(self, task_id, data):
        """
        Execute a request to the OpenAI API
        :param task_id: task id of the current task
        :param data: data object from the broker
        :return:
        """
        logging.info("Executing request")
        if self.p is not None and self.p.is_alive():
            logging.error("Parsr is still running, killing it")
            self.p.terminate()
            self.p = None

        if 'params' not in data:
            data['params'] = {}

        start = time.perf_counter()
        # data['pdf'] is base64 encoded --> save to file
        content = base64.b64decode(data['pdf'])
        with open(self.tmp_file, 'wb') as f:
            f.write(content)

        output_queue = Queue()
        log_queue = StdoutQueue()
        self.p = Process(target=run_parsr,
                         args=(log_queue, output_queue, self.parsr_location, self.tmp_file, data['params']))
        self.p.start()

        while self.p.is_alive():
            # read log output from queue and log it
            while not log_queue.empty():
                log = log_queue.get()
                print(log)
                logging.info(log)
                self.send_status(task_id, log)

        stats = {
            'duration': time.perf_counter() - start
        }

        text, tables = output_queue.get()
        logging.info(text)
        logging.info(tables)

        return text, stats

    def get_input(self):
        """
        Get the input schema
        :return:
        """
        return {
            'data': {
                'pdf': {
                    'type': 'string',
                    'description': 'Base64 encoded PDF file'
                },
                'params': {
                    'type': 'object',
                    'description': 'Additional parameters for the pd3f extraction',
                    'required': False,
                    'properties': {
                        'tables': {
                            'type': 'boolean',
                            'description': 'extract tables via Parsr (with Camelot / Tabula), results into list of CSV strings'
                        },
                        'experimental': {
                            'type': 'boolean',
                            'description': 'leave out duplicate text in headers / footers and turn footnotes to endnotes. Working unreliable right now'
                        },
                        'lang': {
                            'type': 'string',
                            'description': 'set the language, de for German, en for English, es for Spanish, fr for French. Some fast (less accurate) models exists. So set multi-v0-fast to get fast model for German, French (and some other languages)'
                        },
                        'fast': {
                            'type': 'boolean',
                            'description': 'Drop some Parsr steps to speed up computations'
                        },
                    }
                },
            },
            'example': {
                "pdf": "base64 encoded pdf",
                "params": {
                    "tables": True,
                    "experimental": False,
                    "lang": "en",
                    "fast": False
                }
            }
        }

    def get_output(self):
        """
        Get the output schema
        :return:
        """
        return {
            'data': {
            },
            'stats': {
                'type': 'object',
                'properties': {
                    'id': {
                        "type": "string"
                    },
                    'duration': {
                        "type": "number",
                        "description": "Duration of executing azure api in seconds"
                    }
                }
            },
            'example': {
                'stats': {
                    'result': {'id': '123', 'duration': 0.123}
                }
            }
        }
