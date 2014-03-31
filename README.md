# mysql\_null\_driver

Installing a MySQL driver on a machine is sometime a pain, or even impossible.
Furthermore you may want to distribute self contained scripts that access MySQL
without having to ask for additional software installation.

*mysql\_null\_driver* is a pure Python MySQL driver that calls MySQL running the
client on the command line. It was designed so that you may use it by dropping
its module in your source tree or even copy its class in your own source code.

## Installation

To install *mysql\_null\_driver*, you may use one of the following methods:

- Extract its unique class _MysqlNullDriver_ from tarball (in file
  _mysql\_null\_driver/mysql\_null\_driver.py_) and put it in your own source
  code.
- Drop its module (file _mysql\_null\_driver/mysql\_null\_driver.py_ in the
  tarball) in your source directory.
- Install it using PIP, typing _pip imstall mysql\_null\_driver_.
- Install from tarball typing _python setup.py install_.

The Apache license grants you the right to use this driver in any of your
project (even commercial) provided that you mention that you are using
_mysql\_null\_driver_ in your copyright notice.

## Usage

You can use this driver in your code just like so:

```python
from mysql_null_driver import MysqlNullDriver

mysql = MysqlNullDriver(hostname='localhost', database='test',
                        username='test', password='test')
result = mysql.run_query("SHOW DATABASES")
print result
```

When query returns nothing (after an _INSERT_ for instance), method _run\_query()_
will return None. If query returns a result set, this will be a tuple of
dictionaries. For instance, previous sample code could print:

```python
({'Database': 'information_schema'}, {'Database': 'mysql'})
```

Instead of running a query you may run a script as follows:

```python
result = mysql.run_script('my_script.sql')
```

## Parameters

You can have values such as _%(foo)s_ in you query that will be replaced with
corresponding value of the parameters dictionary. For instance:

```python
from mysql_null_driver import MysqlNullDriver

mysql = MysqlNullDriver(hostname='localhost', database='test',
                        username='test', password='test')
parameters = {'name': 'reglisse'}
result = mysql.run_query(query="SELECT * FROM animals WHERE name=%(name)s",
                         parameters=parameters)
print result
```

You may not provide parameters running a script. To do so, call _run\_query()_
with parameters passing query _open('my\_script.sql').read()_.

## Result set types

*mysql\_null\_driver* performs auto casting before returning result sets. As it
calls MySQL on command line, every value in the result set is a string. For
convenience, it casts integers, floats and dates into native Python types.

There are situations where this might not be accurate. For instance, if a
column is of SQL type _VARCHAR(10)_ and contain phone numbers, all its values
will be casted to Python integers. It should not because phone numbers can
start with 0 and it should not be turned to integer.

To avoid this, you may pass cast=False when calling _run\_query()_ or
_run\_script()_, as so:

```python
from mysql_null_driver import MysqlNullDriver

mysql = MysqlNullDriver(hostname='localhost', database='test',
                        username='test', password='test')
result = mysql.run_query("SELECT phone FROM users WHERE name='bob')", cast=False)
print result
```

You may also disable casting when instantiating the driver, passing _cast=False_
to the constructor. This casting configuration will apply on all calls to
_run\_query()_ or _run\_script()_ except if you pass a different value while
calling these methods.

## Last inserted ID

If you need to get ID of the last _INSERT_, just add a call to MySQL function
_last\_insert\_id()_ as so:

```sql
INSERT INTO animals (name, age) VALUES ('Reglisse', 14);
SELECT last_insert_id() AS id;
```

While you run this query, this will return the ID of your last _INSERT_:

```python
({'id': '42'},)
```

## Note

This module is not intended to replace MySQLdb that you SHOULD use if you can
install it on the target machine.

## Releases

- *0.3.1* (2014-03-31): Improved documentation in README for Github.
- *0.3.0* (2014-03-31): Added cast feature and unit tests.
- *0.2.0* (2014-03-26): Improved documentation and module refactoring (to move
  code outside \_\_init\_\_.py module).
- *0.1.0* (2014-03-25): First public release.

Enjoy!
