#   example01.py
#
#   file to demonstrate the use of spMariaDbConnectorPy
#
#
import sys
import os
import random

from global_defines import CONFIG_FILE, MDB_DATA_TABLE_NAME, MDB_DATA_IDS, MDB_DATA_TYPES
from spMariaDbConnectorPy import MariaDbConnector

connector = None
first_rec_id = 0
last_rec_id = 0


print("running Python executable from path", sys.executable)


def prepare_table():
    """Prepares MariaDB table (creates as needed)."""

    print("Preparing MariaDB table.")

    # MariaDB table name
    if len(MDB_DATA_TABLE_NAME) == 0:
        raise Exception('No MDB_DATA_TABLE_NAME defined!')

    # MariaDB data ids
    num_data_ids = len(MDB_DATA_IDS)
    if num_data_ids == 0:
        raise Exception('No MDB_DATA_IDS defined!')

    # may need a data table
    sql = "CREATE TABLE IF NOT EXISTS `" + MDB_DATA_TABLE_NAME + "` (id MEDIUMINT AUTO_INCREMENT"
    for i_id in range(num_data_ids):
        sql += " , `" + MDB_DATA_IDS[i_id] + "` " + MDB_DATA_TYPES[i_id] + " NULL DEFAULT NULL"
    sql += " , PRIMARY KEY (id));"
    connector.execute(sql)


def find_first_record():
    # query for first record
    sql = "SELECT * FROM `" + MDB_DATA_TABLE_NAME + "` ORDER BY `id` LIMIT 1;"
    rec_first = None
    try:
        connector.query(sql)
        rec_first = connector.fetchone()
    except:
        pass
    if rec_first is not None:
        print("First record in run time data:", rec_first)


def find_last_record():
    global last_rec_id
    # query for last record
    sql = "SELECT * FROM `" + MDB_DATA_TABLE_NAME + "` ORDER BY `id` DESC LIMIT 1;"
    rec_last = None
    try:
        connector.query(sql)
        rec_last = connector.fetchone()
    except:
        pass
    if rec_last is not None:
        last_rec_id = rec_last[0]
        print("Last record in run time data:", rec_last)


# =============================================================
# start of prog
# =============================================================
if __name__ == "__main__":

    print("Preparing MariaDB connector.")
    # ensure absolute path independent of CONFIG_FILE being absolute or relative to __file__
    configPath = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
    connector = MariaDbConnector(os.path.abspath(configPath), 'MariaDB')
    connector.connect()

    prepare_table()

    # query fist and last rec
    find_first_record()
    find_last_record()

    # create some data, with None for autoincremented id
    entries = []
    for i in range(5):
        last_rec_id += 1
        name = "user_" + str(last_rec_id)
        value_i = random.randint(200, 500)
        value_f = last_rec_id * value_i * random.random()
        entries.append((None, name, value_i, value_f))

    # then insert list
    sql = "INSERT INTO `" + MDB_DATA_TABLE_NAME + "` VALUES (?, ?, ?, ?)"
    res = connector.executemany(sql, entries)
    if res is None:
        print("adding entries failed with last_error() after INSERT", connector.last_error())

    # find new last record
    find_last_record()

    # query for some records
    start_id = random.randint(1, last_rec_id)
    num_ids = random.randint(3, 7)

    sql = "SELECT * FROM `" + MDB_DATA_TABLE_NAME + "` WHERE `id` >= " + str(start_id) + " ORDER BY `id` LIMIT " + str(num_ids) + ";"
    records = None
    try:
        connector.query(sql)
        records = connector.fetchall()
    except:
        pass
    if records is not None:
        print("Record found >= " + str(start_id) + ":")
        for record in records:
            print(record)

