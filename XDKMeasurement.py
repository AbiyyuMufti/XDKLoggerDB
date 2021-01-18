from datetime import datetime
from queue import Queue
from threading import Thread
import sqlite3


class XDKMeasurementQueue(Queue):
    def __init__(self, sensor_name, sensor_frq):
        self.Name = sensor_name
        self.Size = sensor_frq
        Queue.__init__(self, self.Size)

    def input(self, measurement_time: datetime, measurement_data: list):
        val = "('{}', '{}', {})".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            measurement_time.strftime("%Y-%m-%d %H:%M:%S"),
            ", ".join(measurement_data))
        self.put(val)


class DBInsert(Thread):
    Queries: Queue = Queue(100)

    def __init__(self, queue: XDKMeasurementQueue):
        self.SensorName = queue.Name
        self.insert_cmd = f"INSERT INTO {self.SensorName} VALUES "
        self.queue = queue
        self.values = []
        self.size = queue.Size
        Thread.__init__(self)

    def run(self):
        while True:
            self.values.append(self.queue.get())
            if len(self.values) >= self.size:
                query = self.insert_cmd + ", ".join(self.values)
                # print(query)
                DBInsert.Queries.put(query)
                self.values = []


class DBManager(Thread):
    def __init__(self, database, queries):
        Thread.__init__(self)
        self.db = database
        self.Queries = queries

    def run(self):
        with sqlite3.connect(self.db) as db:
            ptr = db.cursor()
            while True:
                qwr = self.Queries.get()
                # print("inserting")
                ptr.execute(qwr)
                db.commit()
