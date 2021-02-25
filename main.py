import socket
from XDKMeasurement import DBInsert, XDKMeasurementQueue, DBManager
from datetime import datetime

UDP_IP = "192.168.0.73"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

XDKSensorInfos = [("BMA280", 500), ("BME280", 25), ("BMG160", 500), ("BMM150", 20), ("MAX44009", 2), ("AKU340", 10)]
Queues = [XDKMeasurementQueue(sensor, rate) for sensor, rate in XDKSensorInfos]

Tables = [DBInsert(queue) for queue in Queues]
DBM = DBManager("XDK.db", DBInsert.Queries)


if __name__ == '__main__':
    DBM.start()
    for table in Tables:
        table.start()

    while True:
        rxData, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        dataset = str(rxData, "utf-8")

        sensorsData = dataset.split('\t')

        for data in sensorsData:
            incomingData = data.split(';')
            print(incomingData)

            try:
                sensor = incomingData[0]
                measurementTime = datetime.strptime(incomingData[1], "%Y-%m-%dT%H:%M:%SZ")
                measurementData = incomingData[2:]
            except ValueError:
                print("ERROR: INVALID INCOMING BYTES")
                continue

            for q in Queues:
                if sensor == q.Name:
                    q.input(measurementTime, measurementData)
