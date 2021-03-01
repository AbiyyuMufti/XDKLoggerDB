import socket
import traceback
from XDKMeasurement import DBInsert, XDKMeasurementQueue, DBManager
from datetime import datetime, timedelta

UDP_IP = "192.168.0.74"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

XDKSensorInfos = [("BMA280", 100), ("BME280", 100), ("BMG160", 100), ("BMM150", 100), ("MAX44009", 100), ("AKU340", 100)]
# XDKSensorInfos = [("BMA280", 500), ("BME280", 25), ("BMG160", 500), ("BMM150", 20), ("MAX44009", 2), ("AKU340", 10)]
Queues = [XDKMeasurementQueue(sensor, rate) for sensor, rate in XDKSensorInfos]

Tables = [DBInsert(queue) for queue in Queues]

# TODO: Check DB existence and Create DB if not exist yet
DBM = DBManager("XDK.db", DBInsert.Queries)


if __name__ == '__main__':
    DBM.start()
    for table in Tables:
        table.start()

    counter = 0
    workTime = datetime.now()

    while True:
        start = datetime.now()

        rxData, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        dataset = str(rxData, "utf-8")
        dataRaw = dataset.split('\t')
        #print(dataRaw)

        stop = datetime.now()
        dT = stop - start
        if dT > timedelta(seconds=1):
            counter = counter + 1
            resetTime = start
            ActiveDuration = resetTime - workTime
            print("Active time\t:", ActiveDuration)
            workTime = stop
            # after reset
            print("Reset at\t:", start.time())
            print("Start at\t:", stop.time())
            ResetDuration = stop - start
            print("Reset time\t:", ResetDuration)

        if len(dataRaw) > 1:
            time = dataRaw[0]
            sensorsData = dataRaw[1:]
        else:
            sensorsData = dataRaw

        for data in sensorsData:
            incomingData = data.split(';')
            # print(incomingData)

            try:
                sensor = incomingData[0]
                if len(dataRaw) > 1:
                    measurementTime = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
                    measurementData = incomingData[1:]
                else:
                    measurementTime = datetime.strptime(incomingData[1], "%Y-%m-%dT%H:%M:%SZ")
                    measurementData = incomingData[2:]
            except ValueError:
                # print("ERROR: INVALID INCOMING BYTES")
                # traceback.print_exc()
                continue

            for q in Queues:
                if sensor == q.Name:
                    q.input(measurementTime, measurementData)