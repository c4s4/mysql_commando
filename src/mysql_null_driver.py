#!/usr/bin/env python
# encoding: UTF-8

from __future__ import with_statement
import datetime
import subprocess


#pylint: disable=E1103
class MysqlNullDriver(object):

    ISO_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, configuration=None,
                 hostname=None, database=None,
                 username=None, password=None,
                 charset=None):
        if hostname and database and username and password:
            self.hostname = hostname
            self.database = database
            self.username = username
            self.password = password
            if charset:
                self.charset = charset
            else:
                self.charset = None
        elif configuration:
            self.hostname = configuration['hostname']
            self.database = configuration['database']
            self.username = configuration['username']
            self.password = configuration['password']
            if 'charset' in configuration:
                self.charset = configuration['charset']
            else:
                self.charset = None
        else:
            raise Exception('Missing database configuration')

    def run_query(self, query, parameters=None):
        query = self.process_parameters(query, parameters)
        if self.charset:
            command = ['mysql',
                       '-u%s' % self.username,
                       '-p%s' % self.password,
                       '-h%s' % self.hostname,
                       '--default-character-set', self.charset,
                       '-B', '-e', query, self.database]
        else:
            command = ['mysql',
                       '-u%s' % self.username,
                       '-p%s' % self.password,
                       '-h%s' % self.hostname,
                       '-B', '-e', query, self.database]
        output = self._execute_with_output(command)
        if output:
            result = []
            lines = output.strip().split('\n')
            fields = lines[0].split('\t')
            for line in lines[1:]:
                values = line.split('\t')
                result.append(dict(zip(fields, values)))
            return tuple(result)

    def run_script(self, script):
        if self.charset:
            command = ['mysql',
                       '-u%s' % self.username,
                       '-p%s' % self.password,
                       '-h%s' % self.hostname,
                       '--default-character-set', self.charset,
                       '-B', self.database]
        else:
            command = ['mysql',
                       '-u%s' % self.username,
                       '-p%s' % self.password,
                       '-h%s' % self.hostname,
                       '-B', self.database]
        with open(script) as stdin:
            output = self._execute_with_output(command, stdin=stdin)
        if output:
            result = []
            lines = output.strip().split('\n')
            fields = lines[0].split('\t')
            for line in lines[1:]:
                values = line.split('\t')
                result.append(dict(zip(fields, values)))
            return tuple(result)

    @staticmethod
    def _execute_with_output(command, stdin=None):
        if stdin:
            process = subprocess.Popen(command, stdout=subprocess.PIPE,  stderr=subprocess.PIPE, stdin=stdin)
        else:
            process = subprocess.Popen(command, stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        output, errput = process.communicate()
        if process.returncode != 0:
            raise Exception(errput.strip())
        return output

    @staticmethod
    def process_parameters(query, parameters):
        if not parameters:
            return query
        if isinstance(parameters, (list, tuple)):
            parameters = tuple(MysqlNullDriver.format_parameters(parameters))
        elif isinstance(parameters, dict):
            parameters = dict(zip(parameters.keys(), MysqlNullDriver.format_parameters(parameters.values())))
        return query % parameters

    @staticmethod
    def format_parameters(parameters):
        return [MysqlNullDriver.format_parameter(param) for param in parameters]

    @staticmethod
    def format_parameter(parameter):
        if isinstance(parameter, (int, long, float)):
            return str(parameter)
        elif isinstance(parameter, (str, unicode)):
            return "'%s'" % MysqlNullDriver.escape_string(parameter)
        elif isinstance(parameter, datetime.datetime):
            return "'%s'" % parameter.strftime(MysqlNullDriver.ISO_FORMAT)
        else:
            raise Exception("Type '%s' is not managed as a query parameter" % parameter.__class__.__name__)

    @staticmethod
    def escape_string(string):
        return string.replace("'", "''")

