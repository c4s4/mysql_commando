#!/usr/bin/env python
# encoding: UTF-8

from __future__ import with_statement
import re
import datetime
import subprocess


#pylint: disable=E1103
class MysqlNullDriver(object):

    ISO_FORMAT = '%Y-%m-%d %H:%M:%S'
    CASTS = {
        r'-?\d+': int,
        r'-?\d*\.?\d*(E-?\d+)?': float,
        r'\d{4}-\d\d-\d\d \d\d:\d\d:\d\d': lambda d: datetime.datetime.strptime(MysqlNullDriver.ISO_FORMAT, d),
    }

    def __init__(self, configuration=None,
                 hostname=None, database=None,
                 username=None, password=None,
                 charset=None, cast=False):
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
        self.cast = cast

    def run_query(self, query, parameters=None):
        query = self._process_parameters(query, parameters)
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
            return self._output_to_result(output)

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
            return self._output_to_result(output)
    
    def _output_to_result(self, output):
        result = []
        lines = output.strip().split('\n')
        fields = lines[0].split('\t')
        for line in lines[1:]:
            values = line.split('\t')
            if self.cast:
                values = MysqlNullDriver._cast_list(values)
            result.append(dict(zip(fields, values)))
        return tuple(result)
    
    @staticmethod
    def _cast_list(values):
        return [MysqlNullDriver._cast(value) for value in values]
    
    @staticmethod
    def _cast(value):
        for regexp in MysqlNullDriver.CASTS:
            if re.match("^%s$" % regexp, value):
                return MysqlNullDriver.CASTS[regexp](value)
        return value
    
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
    def _process_parameters(query, parameters):
        if not parameters:
            return query
        if isinstance(parameters, (list, tuple)):
            parameters = tuple(MysqlNullDriver._format_parameters(parameters))
        elif isinstance(parameters, dict):
            parameters = dict(zip(parameters.keys(), MysqlNullDriver._format_parameters(parameters.values())))
        return query % parameters

    @staticmethod
    def _format_parameters(parameters):
        return [MysqlNullDriver._format_parameter(param) for param in parameters]

    @staticmethod
    def _format_parameter(parameter):
        if isinstance(parameter, (int, long, float)):
            return str(parameter)
        elif isinstance(parameter, (str, unicode)):
            return "'%s'" % MysqlNullDriver._escape_string(parameter)
        elif isinstance(parameter, datetime.datetime):
            return "'%s'" % parameter.strftime(MysqlNullDriver.ISO_FORMAT)
        else:
            raise Exception("Type '%s' is not managed as a query parameter" % parameter.__class__.__name__)

    @staticmethod
    def _escape_string(string):
        return string.replace("'", "''")
