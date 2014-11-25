#!/usr/bin/env python
# encoding: UTF-8

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
import unittest
import datetime
from mysql_commando import MysqlCommando


#pylint: disable=W0212
class TestMysqlCommando(unittest.TestCase):

    CONFIG = {
        'hostname': 'localhost',
        'database': 'test',
        'username': 'test',
        'password': 'test',
    }
    SQL_DIR = os.path.join(os.path.dirname(__file__), 'sql')

    def test_run_query_nominal(self):
        mysql = MysqlCommando(configuration=self.CONFIG)
        result = mysql.run_query("SHOW DATABASES;")
        self.assertTrue('information_schema' in [entry['Database'] for entry in result])

    def test_run_query_error(self):
        mysql = MysqlCommando(configuration=self.CONFIG)
        try:
            mysql.run_query("BAD SQL QUERY;")
            self.fail('Should have failed')
        except Exception, e:
            self.assertTrue("You have an error in your SQL syntax" in e.message)

    def test_run_script_nominal(self):
        script = os.path.join(self.SQL_DIR, 'test_mysql_commando.sql')
        mysql = MysqlCommando(configuration=self.CONFIG)
        expected = ({'id': 1, 'name': 'Réglisse', 'age': 14},)
        actual = mysql.run_script(script)
        self.assertEqual(expected, actual)

    def test_run_script_error(self):
        mysql = MysqlCommando(configuration=self.CONFIG)
        try:
            mysql.run_script("script_that_doesnt_exist.sql")
            self.fail('Should have failed')
        except Exception, e:
            self.assertTrue("No such file or directory: 'script_that_doesnt_exist.sql'" in str(e))

    def test_run_script_syntax_error(self):
        script = os.path.join(self.SQL_DIR, 'test_mysql_commando_error.sql')
        mysql = MysqlCommando(configuration=self.CONFIG)
        try:
            mysql.run_script(script)
            self.fail('Should have failed')
        except Exception, e:
            self.assertTrue("You have an error in your SQL syntax" in e.message)

    def test_process_parameters(self):
        query = "%s %s %s"
        parameters = [1, 'deux', datetime.datetime(2014, 01, 22, 13, 10, 33)]
        expected = "1 'deux' '2014-01-22 13:10:33'"
        actual = MysqlCommando._process_parameters(query, parameters) #pylint: disable=W0212
        self.assertEqual(expected, actual)

    def test_cast(self):
        expected = 1
        actual = MysqlCommando._cast("1")
        self.assertEqual(expected, actual)
        expected = 1.23
        actual = MysqlCommando._cast("1.23")
        self.assertEqual(expected, actual)
        expected = 1.23e-45
        actual = MysqlCommando._cast("1.23e-45")
        self.assertEqual(expected, actual)
        expected = datetime.datetime(2014, 3, 29, 11, 18, 0)
        actual = MysqlCommando._cast('2014-03-29 11:18:00')
        self.assertEqual(expected, actual)
        expected = 'test'
        actual = MysqlCommando._cast('test')
        self.assertEqual(expected, actual)
        expected = None
        actual = MysqlCommando._cast('NULL')
        self.assertEqual(expected, actual)

    def test_cast_query(self):
        driver = MysqlCommando(configuration=self.CONFIG)
        driver.run_script(os.path.join(self.SQL_DIR, 'test_mysql_commando_cast_query.sql'))
        expected = (
            {'i': 123, 'f': 1.23, 'd': datetime.datetime(2014, 3, 29, 11, 18, 0), 's': 'test'},
            {'i': -456, 'f': -1.2e-34, 'd': datetime.datetime(2014, 3, 29), 's': ' 123'},
        )
        actual = driver.run_query("SELECT i, f, d, s FROM test", cast=True)
        self.assertEqual(expected, actual)
        driver.run_script(os.path.join(self.SQL_DIR, 'test_mysql_commando_cast_query.sql'))
        expected = (
            {'i': '123', 'f': '1.23', 'd': '2014-03-29 11:18:00', 's': 'test'},
            {'i': '-456', 'f': '-1.2e-34', 'd': '2014-03-29 00:00:00', 's': ' 123'},
        )
        actual = driver.run_query("SELECT i, f, d, s FROM test", cast=False)
        self.assertEqual(expected, actual)

    def test_last_insert_id(self):
        driver = MysqlCommando(configuration=self.CONFIG)
        driver.run_script(os.path.join(self.SQL_DIR, 'test_mysql_commando_last_insert_id.sql'))
        expected = 1
        actual = driver.run_query("INSERT INTO test (name, age) VALUES ('Reglisse', 14)", last_insert_id=True)
        self.assertEqual(expected, actual)
        expected = ({'id': 2},)
        actual = driver.run_script(os.path.join(self.SQL_DIR, 'test_mysql_commando_last_insert_id_insert.sql'))
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

