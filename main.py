import socket
from XDKMeasurement import DBInsert, XDKMeasurementQueue, DBManager
from datetime import datetime

UDP_IP = "192.168.178.24"
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
        rxData, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        dataset = str(rxData, "utf-8")
        dataRaw = dataset.split('\t')

        # get time sntp or rtc - time in xdk --> if the value default then use python time
        measurementTime = datetime.strptime(dataRaw[0], "%Y-%m-%dT%H:%M:%SZ") \
            if "2000-01-01T00:00:00Z" != dataRaw[0] else datetime.now()
        sensorsData = dataRaw[1:]

        for data in sensorsData:
            incomingData = data.split(';')
            try:
                measurementName = incomingData[0]
                measurementData = incomingData[1:]
            except ValueError:
                continue

            for q in Queues:
                if measurementName == q.Name:
                    q.input(measurementTime, measurementData)
