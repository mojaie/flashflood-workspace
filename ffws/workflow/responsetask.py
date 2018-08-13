#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import glob
import gzip
import json
import os
import time

from flashflood import static
from flashflood.core.task import Task
from flashflood.lod import ListOfDict

from ffws import configparser as conf


TASK_LIFETIME = 86400 * 7  # Time(sec)


class ResponseTask(Task):
    def on_finish(self):
        super().on_finish()
        self.save()

    def on_abort(self):
        super().on_abort()
        self.save()

    def save(self):
        for lpath in glob.glob(os.path.join(conf.TEMP_DIR, '*.json.gz')):
            with gzip.open(lpath, 'rt') as f:
                tmp = json.load(f)
            finished = time.mktime(
                time.strptime(tmp["created"], "%X %x %Z")) + tmp["execTime"]
            if finished + TASK_LIFETIME < time.time():
                os.remove(lpath)
        dpath = os.path.join(conf.TEMP_DIR, '{}.json.gz'.format(self.id))
        with gzip.open(dpath, 'wt') as f:
            f.write(json.dumps(self.response()))

    def response(self):
        return {
            "$schema": static.JOB_RESULT_SCHEMA,
            "workflowID": self.id,
            "name": self.specs.name,
            "query": self.specs.query,
            "created": time.strftime("%X %x %Z",
                                     time.localtime(self.creation_time)),
            "status": self.status,
            "progress": self.progress(),
            "execTime": self.execution_time(),
            "fields": self.set_fields(),
            "records": self.specs.results.records
        }

    def set_fields(self):
        fields = ListOfDict(self.specs.results.fields)
        new_fields = ListOfDict()
        idx = fields.pick("key", "index")
        if idx:
            new_fields.add(idx)
        struct = fields.pick("key", "structure")
        if struct:
            new_fields.add(struct)
        # set hidden fields
        for f in fields:
            if not f["key"].startswith("__"):
                new_fields.add(f)
        # set default invisible fields
        for f in new_fields:
            if f["key"].startswith("_"):
                f["visible"] = False
        return new_fields

    def progress(self):
        if self.status == "done":
            return 100
        if self.status in ("running", "interrupted", "aborted"):
            try:
                p = self.specs.done_count.value / self.specs.input_size.value
            except ZeroDivisionError:
                return
            return round(p * 100, 1)
        else:
            return 0
