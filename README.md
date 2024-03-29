# XDKLoggerDB

## Description
A python program that receives the measurement data from the XDKDataLogger and then store it inside a local database. The measurement data are received via UDP Protocol and the sqlite3 database is used.
![image](https://github.com/AbiyyuMufti/XDKDataLogger/blob/master/images/GlobalProgramFlow.png)

This repository currenty existing of three python scripts:
1. *createDB.py* is a script to create databse if none exists yet.
2. *XDKMeasurement.py* is a module that handels the logging process to the database.
3. *main.py* is the main program, which read the BOSCH XDK measurement data from UDP port.

## Creating Database
If there is no existing Database for the XDKDataLogger, the python program *createDB.py* is supposed to be run. In thes script the function to create a database connection and to create database table using sqlite3 library is implemented. Moreover, the SQL commands for creating specific table that are compatible to the XDKDataLogger is also declared in this script.

Lastly in this script, at the ```if __name__ == ‘__main__’:``` section, the creation of DB connection and table creation will be executed. The result is an empty database called “XDK.db” with compatible tables for each sensor unit in XDK.
For further improvement, the *main.py* program could also implement a functionality that check if the database that is compatible for XDK already exists. If that the case then the program should use that database as the storage, otherwise a new empty database with compatible tables should be created first.

## Storing data inside database
A module for the storing the XDK measurement data is packed inside the *XDKMeasurement.py* script. Here there are 3 Classes implemented to do receive the measurement data from XDK, put it inside queues and with parallel threads storing the data to the database.

### Class XDKMeasurementQueue
This class is a child class of Queue object. The purpose of this class is to store the measurement data that are received from the UDP Port before putting it to the database. The reason Queue are needed is because the UDP reading could be very fast while the process to put it into the database could on the other hand running a bit slow. This queue ensures that the UDP read flow and the database storage process do not distract or interfere with each other but still connected with a secure thread.

When an instance of XDKMeasurementQueue is initialize, its demand the name and the frequency. This will come in handy for each sensor, so each sensor can have its own queue.
With the *input()* function, the measurement time and the measurement data that are received via UDP can be stored safely into the queue directly using a format of the argument of the SQL command to store the data.

### Class DBInsert
This class is a child class of Thread object. The purpose of this class is to create and run the thread for inserting data reading from the XDKMeasurementQueue to another Queues that store the global queries for storing to database. Just like the previous class, this class also allows each sensor group to store the measurement data in different threads. 
Inside the *run()* function, a forever loop is exists. In this forever loop the process wait for the XDKMeasurementQueue to be filled with data. After the XDKMeasurementQueue exceeding specified size, an SQL Queries that containing command to insert multiple data at the same time are creating. These queries are lastly put inside a class object queue named Queries.

### Class DBManager
This class is also a child class of Thread object. The purpose of this class is to maintain the database connection and store the information using the queries inside the queue from the DBInsert object to the database. This class allows the storing process to the database faster and more efficient without disturbing the data stream from UDP Port. Using the run() function, the process will wait until a query inside the queue is exists. Then this query will be executed.

## Main Program Flow
In the main program flow the 3 classes inside the XDKMeasurement module are instantiate. Using a list of the XDKSensorInfos, the Queues for each sensor are created using XDKMeasurementQueue class.
The next step is creating multiple threads for each sensor group and then collecting the queries from each sensor group and put them inside a queue using DBInsert object.
To manage the Database connection. An object DBManager is also created in its own thread. This thread will wait until a query inside the DBInsert.Queries exist and then execute that query.
In the ```if __name__ == ‘__main__’:``` section, the DBManager thread is started at the very first followed by the threads of each sensors using DBInsert. Furthermore, a forever loop for UDP data reading is running. In each loop, the program will wait until the data from the UDP port are being received, then this raw data will be splited into its specific information.
The data is separated first with tab then you got the multiple groups of sensor measurement and a timestamp. 
The string that received should follow this convention:
```
(timestamp)\t(sensor_data_1)\t(sensor_data2)…(sensor_data_n)
```
During the reading, XDK is allowed to send at the least 1 sensor data or more with maxsimum 6 sensor data at the same reading and some other sensor data at different time. The data can still be read and classified very easily, because the convention is the same. With only using simple for loop is enough to distribute the data into its own database table group.

The data of sensor measurement is on the other hand separated with semicolon. This data containing the name of the sensor and its measurement value.
The string of the sensor measurement should follow this convention:
```
(name_sensor);(data_1); ..;(data_n)
```
This information will be split and appended to the query using DBInsert object.
