#!/usr/bin/env python
# encoding: UTF-8

from __future__ import with_statement
import re
import datetime
import subprocess


#pylint: disable=E1103
class MysqlCommando(object):

    ISO_FORMAT = '%Y-%m-%d %H:%M:%S'
    CASTS = (
        (r'-?\d+', int),
        (r'-?\d*\.?\d*([Ee][+-]?\d+)?', float),
        (r'\d{4}-\d\d-\d\d \d\d:\d\d:\d\d', lambda d: datetime.datetime.strptime(d, MysqlCommando.ISO_FORMAT)),
    )
    QUERY_LAST_INSERT_ID = """
    ;SELECT last_insert_id() as last_insert_id;
    """

    def __init__(self, configuration=None,
                 hostname=None, database=None,
                 username=None, password=None,
                 encoding=None, cast=True):
        if hostname and database and username and password:
            self.hostname = hostname
            self.database = database
            self.username = username
            self.password = password
            if encoding:
                self.encoding = encoding
            else:
                self.encoding = None
        elif configuration:
            self.hostname = configuration['hostname']
            self.database = configuration['database']
            self.username = configuration['username']
            self.password = configuration['password']
            if 'encoding' in configuration:
                self.encoding = configuration['encoding']
            else:
                self.encoding = None
        else:
            raise Exception('Missing database configuration')
        self.cast = cast

    def run_query(self, query, parameters=None, cast=None,
                  last_insert_id=False):
        query = self._process_parameters(query, parameters)
        if last_insert_id:
            query += self.QUERY_LAST_INSERT_ID
        if self.encoding:
            command = ['mysql',
                       '-u%s' % self.username,
                       '-p%s' % self.password,
                       '-h%s' % self.hostname,
                       '--default-character-set', self.encoding,
                       '-B', '-e', query, self.database]
        else:
            command = ['mysql',
                       '-u%s' % self.username,
                       '-p%s' % self.password,
                       '-h%s' % self.hostname,
                       '-B', '-e', query, self.database]
        output = self._execute_with_output(command)
        if cast is None:
            cast = self.cast
        if output:
            result = self._output_to_result(output, cast=cast)
            if last_insert_id:
                return int(result[0]['last_insert_id'])
            else:
                return result

    def run_script(self, script, cast=None):
        if self.encoding:
            command = ['mysql',
                       '-u%s' % self.username,
                       '-p%s' % self.password,
                       '-h%s' % self.hostname,
                       '--default-character-set', self.encoding,
                       '-B', self.database]
        else:
            command = ['mysql',
                       '-u%s' % self.username,
                       '-p%s' % self.password,
                       '-h%s' % self.hostname,
                       '-B', self.database]
        if cast is None:
            cast = self.cast
        with open(script) as stdin:
            output = self._execute_with_output(command, stdin=stdin)
        if output:
            return self._output_to_result(output, cast=cast)

    def _output_to_result(self, output, cast):
        if self.encoding:
            output = unicode(output, encoding=self.encoding, errors='replace')
        else:
            output = unicode(output, errors='replace')
        result = []
        lines = output.strip().split('\n')
        fields = lines[0].split('\t')
        for line in lines[1:]:
            values = line.split('\t')
            if cast:
                values = MysqlCommando._cast_list(values)
            result.append(dict(zip(fields, values)))
        return tuple(result)

    @staticmethod
    def _cast_list(values):
        return [MysqlCommando._cast(value) for value in values]

    @staticmethod
    def _cast(value):
        for regexp, function in MysqlCommando.CASTS:
            if re.match("^%s$" % regexp, value):
                return function(value)
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
            parameters = tuple(MysqlCommando._format_parameters(parameters))
        elif isinstance(parameters, dict):
            parameters = dict(zip(parameters.keys(), MysqlCommando._format_parameters(parameters.values())))
        return query % parameters

    @staticmethod
    def _format_parameters(parameters):
        return [MysqlCommando._format_parameter(param) for param in parameters]

    @staticmethod
    def _format_parameter(parameter):
        if isinstance(parameter, (int, long, float)):
            return str(parameter)
        elif isinstance(parameter, (str, unicode)):
            return "'%s'" % MysqlCommando._escape_string(parameter)
        elif isinstance(parameter, datetime.datetime):
            return "'%s'" % parameter.strftime(MysqlCommando.ISO_FORMAT)
        else:
            raise Exception("Type '%s' is not managed as a query parameter" % parameter.__class__.__name__)

    @staticmethod
    def _escape_string(string):
        return string.replace("'", "''")
