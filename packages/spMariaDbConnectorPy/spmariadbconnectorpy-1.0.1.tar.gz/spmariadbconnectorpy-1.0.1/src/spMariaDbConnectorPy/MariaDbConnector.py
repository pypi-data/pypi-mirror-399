# ================================================================================
#
#   MariaDbConnector class
#
#   object for dealing with MariaDB operations
#
#   MIT License
#
#   Copyright (c) 2025 krokoreit (krokoreit@gmail.com)
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.
#
# ================================================================================



import mariadb
import os
from collections.abc import Sequence
import configparser


class MariaDbConnector():
    def __init__(self, config_file, config_section):

        if not os.path.isfile(config_file):
            raise Exception ('Config file', config_file, 'does not exist.')

        config = configparser.ConfigParser(inline_comment_prefixes='#', empty_lines_in_values=False)
        config.read(config_file)        

         # whether to output debug strings, false by default
        self._debug = config[config_section].getboolean('debug', 0)
        # host and port to connect to
        self._host = config[config_section].get('host', 'localhost')
        self._port = config[config_section].getint('port', 3306)
        # user name and password to use
        self._username = config[config_section].get('username', 'root')
        self._password = config[config_section].get('password', 'root')
        # database name
        self._db_name = config[config_section].get('db_name', 'my_db_name')
        self._cnx = None
        self._cursor = None
        self._last_error = None

    
    def connect(self):
        """Creates a connection"""
        if self._cnx is not None:
            return False
        
        try:
            self._cnx = mariadb.connect(
                    host=self._host,
                    port=self._port,
                    user=self._username,
                    password=self._password,
                    database=self._db_name
                )
            return True

        except Exception as e:
            print("Error in", __class__.__name__, "connect() to", self._db_name, ":", str(e))
            return False



    def disconnect(self):
        """Closes the connection"""
        try:
            if self._cursor is not None:
                self._cursor.close()
                self._cursor = None
            if self._cnx is not None:
                self._cnx.close()      
                self._cnx = None

        except Exception as e:
            print("Error in", __class__.__name__, "disconnect() from", self._db_name, ":", str(e))


    def begin(self):
        "Starts a new transaction which can be committed by commit() or cancelled by rollback()."

        try:
            if self._cnx is None:
                if not self.connect():
                    raise Exception("Failed to create connection.")                
            self._cnx.begin()
        except Exception as e:
            print("Error in", __class__.__name__, "begin():", str(e))


    def commit(self):
        """Commits a pending transaction to the database."""

        try:
            # must have connection
            if self._cnx is not None:
                self._cnx.commit()
        except Exception as e:
            print("Error in", __class__.__name__, "commit():", str(e))


    def rollback(self):
        """Rolls back a transaction."""

        try:
            # must have connection
            if self._cnx is not None:
                self._cnx.rollback()
        except Exception as e:
            print("Error in", __class__.__name__, "rollback():", str(e))


    def cursor(self, cursorclass=mariadb.cursors.Cursor, **kwargs):
        """Creates a connection and returns a cursor to be used directly with the 
        MariaDB cursor functions (i.e. not using functions of this class). 
        Must call disconnect() to close connection and cursor when no longer used."""

        try:
            if self._cnx is None:
                if not self.connect():
                    raise Exception("Failed to create connection.")
                
            return self._cnx.cursor(cursorclass, **kwargs)

        except Exception as e:
            print("Error in", __class__.__name__, "cursor():", str(e))
            return None


    def execute(self, sql, data: Sequence = (), prevent_auto_commit = False, buffered=None):
        """Calls cursor.execute(sql, data) and returns True for succesful execution. In case
            of failure, check last_error() for details about the error. Use prevent_auto_commit = True 
            for transactions to remain uncommitted."""

        execute_ok = True
        self._last_error = None

        # disconnect when there was no prior connection 
        auto_disconnect = self.connect()

        try:
            if self._cursor is None:
                self._cursor = self._cnx.cursor()
            self._cursor.execute(sql, data, buffered)
            if not prevent_auto_commit:
                self._cnx.commit()
        except Exception as e:
            execute_ok = False
            self._last_error = "Error in " + __class__.__name__ + " execute() in " + self._db_name + " with SQL='" + sql + "': " + str(e)
            print(self._last_error)

        if auto_disconnect:
            self.disconnect()

        return execute_ok


    def executemany(self, sql, data, prevent_auto_commit = False):
        """Calls cursor.executemany(sql, data) and returns True for succesful execution. In case
            of failure, check last_error() for details about the error. Use prevent_auto_commit = True 
            for transactions to remain uncommitted."""

        execute_ok = True
        self._last_error = None

        # disconnect when there was no prior connection 
        auto_disconnect = self.connect()

        try:
            if self._cursor is None:
                self._cursor = self._cnx.cursor()
            self._cursor.executemany(sql, data)
            if not prevent_auto_commit:
                self._cnx.commit()
        except Exception as e:
            execute_ok = False
            self._last_error = "Error in " + __class__.__name__ + " executemany() in " + self._db_name + " with SQL='" + sql + "': " + str(e)
            print(self._last_error)

        if auto_disconnect:
            self.disconnect()

        return execute_ok


    def query(self, sql, data: Sequence = (), buffered=None):
        """Creates a connection and cursor object before executing the sql query for
        results to be fetched by the fetch functions of this class.
        Returns True for succesful execution. In case of failure, check last_error() for
        details about the error.
        Must call disconnect() to close connection and cursor when no longer used."""

        execute_ok = True
        self._last_error = None

        try:
            if self._cnx is None:
                if not self.connect():
                    raise Exception("Failed to create connection.")
                
            if self._cursor is None:
                self._cursor = self._cnx.cursor()

            self._cursor.execute(sql, data, buffered)

        except Exception as e:
            execute_ok = False
            self._last_error = "Error in " + __class__.__name__ + " query(): " + str(e) + " with sql = " + sql
            print(self._last_error)

        return execute_ok


    def fetchone(self):
        """Calls cursor.fetchone() to fetch the next row of a query result set, 
        returning a single sequence, or None if no more data is available.
        None is also returned, when an error occurs, e.g. when the previous call to
        query() / execute() didn't produce a result set or query() / execute() wasn't called before.
        Therefore, when None is returned, check for 'last_error() is None' to confirm that
        there are really no more data available.
        """

        self._last_error = None

        try:
            if self._cursor is not None:
                return self._cursor.fetchone()
            else:
                raise Exception("Trying to fetch data without prior query()!")
        except Exception as e:
            self._last_error = "Error in " + __class__.__name__ + " fetchone(): " + str(e)
            print(self._last_error)
            return None


    def fetchmany(self, size: int = 0):
        """Calls cursor.fetchmany() to fetch the next set of rows of a query result, 
        returning a sequence of sequences (e.g. a list of tuples). An empty sequence 
        is returned when no more rows are available.

        The number of rows to fetch per call is specified by the size parameter.
        If it is not given, the cursor's arraysize determines the number
        of rows to be fetched. The method should try to fetch as many rows
        as indicated by the size parameter. If this is not possible due to the 
        specified number of rows not being available, fewer rows may be returned.

        When an error occurs, e.g. the previous call to query() / execute() didn't
        produce a result set or query() / execute() wasn't called before, None is returned.
        """

        self._last_error = None

        try:
            if self._cursor is not None:
                return self._cursor.fetchmany(size)
            else:
                raise Exception("Trying to fetch data without prior query()!")
        except Exception as e:
            self._last_error = "Error in " + __class__.__name__ + " fetchmany(): " + str(e)
            print(self._last_error)
            return None


    def fetchall(self):
        """Calls cursor.fetchall() to fetch all remaining rows of a query result, 
        returning them as a sequence of sequences (e.g. a list of tuples).

        When an error occurs, e.g. the previous call to query() / execute() didn't
        produce a result set or query() / execute() wasn't called before, None is returned.
        """

        self._last_error = None

        try:
            if self._cursor is not None:
                return self._cursor.fetchall()
            else:
                raise Exception("Trying to fetch data without prior query()!")
        except Exception as e:
            self._last_error = "Error in " + __class__.__name__ + " fetchall(): " + str(e)
            print(self._last_error)
            return None


    def get_rowcount(self):
        """ReturnsReturns the number of rows of the cursor after running execute statements."""

        if self._cursor is None:
            return 0
        return self._cursor.rowcount



    def last_error(self):
        """Returns the last error from a previous operation."""
        return self._last_error
