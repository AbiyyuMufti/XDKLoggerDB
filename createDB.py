import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


AKU_CREATE = """create table IF NOT EXISTS AKU340
(
    incomingTime    timestamp default current_timestamp,
    measurementTime datetime,
    NoiseRMS        numeric,
    PressureLevel   numeric
);"""

BMA_CREATE = """create table IF NOT EXISTS BMA280
(
    incomingTime    timestamp default current_timestamp,
    measurementTime datetime,
    xAxisData       numeric,
    yAxisData       numeric,
    zAxisData       numeric
);"""

BME_CREATE = """create table IF NOT EXISTS BME280
(
    incomingTime    timestamp default current_timestamp,
    measurementTime datetime,
    pressure        numeric,
    temperature     numeric,
    humidity        numeric
);"""

BMG_CREATE = """create table IF NOT EXISTS BMG160
(
    incomingTime    timestamp default current_timestamp,
    measurementTime datetime,
    xAxisData       numeric,
    yAxisData       numeric,
    zAxisData       numeric
);"""

BMM_CREATE = """create table IF NOT EXISTS BMM150
(
    incomingTime    timestamp default current_timestamp,
    measurementTime datetime,
    xAxisData       numeric,
    yAxisData       numeric,
    zAxisData       numeric
);"""


MAX_CREATE = """create table IF NOT EXISTS MAX44009
(
    incomingTime    timestamp default current_timestamp,
    measurementTime datetime,
    lightIntensity  numeric
);"""


CREATE_LIST = [AKU_CREATE, BMA_CREATE, BME_CREATE, BMG_CREATE, BMM_CREATE, MAX_CREATE]

if __name__ == '__main__':
    conn = create_connection("XDK.db")
    for tab in CREATE_LIST:
        create_table(conn, tab)
