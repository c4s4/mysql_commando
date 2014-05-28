=================
mysql_commando
=================

Installing a MySQL driver on a machine is sometime a pain, or even impossible.
Furthermore you may want to distribute self contained scripts that access MySQL
without having to ask for additional software installation.

**mysql_commando** is a pure Python MySQL driver that calls MySQL running
the client on the command line. It was designed so that you may use it by
dropping its module in your source tree or even copy its class in your own
source code.

Installation
============

To install **mysql_commando**, you may use one of the following methods:

- Extract its unique class ``MysqlCommando`` from tarball (in file
  *mysql_commando/mysql_commando.py*) and put it in your own source code.
- Drop its module (file *mysql_commando/mysql_commando.py* in the tarball)
  in your source directory.
- Install it using PIP, typing ``pip install mysql_commando``.
- Install from tarball typing ``python setup.py install``.

The Apache license grants you a right to use this driver in any of your project
(even commercial) provided that you mention that you are using
**mysql_commando** in your copyright notice.

Usage
=====

You can use this driver in your code just like so::

    from mysql_commando import MysqlCommando
    
    mysql = MysqlCommando(hostname='localhost', database='test',
                          username='test', password='test')
    result = mysql.run_query("SHOW DATABASES")
    print result

When query returns nothing (after an ``INSERT`` for instance), method
``run_query()`` will return ``None``. If query returns a result set, this will
be a tuple of dictionaries. For instance, previous sample code could print::

    ({'Database': 'information_schema'}, {'Database': 'mysql'})

Instead of running a query you may run a script as follows::

    result = mysql.run_script('my_script.sql')

Parameters
==========

You can have values such as ``%(foo)s`` in you query that will be replaced
with corresponding value of the parameters dictionary. For instance::

    from mysql_commando import MysqlCommando

    mysql = MysqlCommando(hostname='localhost', database='test',
                          username='test', password='test')
    parameters = {'name': 'reglisse'}
    result = mysql.run_query(query="SELECT * FROM animals WHERE name=%(name)s",
                             parameters=parameters)
    print result

You may not provide parameters running a script. To do so, call ``run_query()``
with parameters passing query ``open('my_script.sql').read()``.

Result set types
================

**mysql_commando** performs auto casting before returning result sets. As it
calls MySQL on command line, every value in the result set is a string. For
convenience, it casts integers, floats and dates into native Python types.

There are situations where this might not be accurate. For instance, if a column
is of SQL type ``VARCHAR(10)`` and contain phone numbers, all its values will be
casted to Python integers. It should not because phone numbers can start with
*0* and it should not be turned to integer.

To avoid this, you may pass ``cast=False`` when calling ``run_query()`` or
``run_script()``, like so::

    from mysql_commando import MysqlCommando
    
    mysql = MysqlCommando(hostname='localhost', database='test',
                          username='test', password='test')
    result = mysql.run_query("SELECT phone FROM users WHERE name='bob')", cast=False)
    print result

You may also disable casting when instantiating the driver, passing
``cast=False`` to the constructor. This casting configuration will apply on all
calls to ``run_query()`` or ``run_script()`` except if you pass a different
value while calling these methods.

Last insert ID
==============

To get the ID of the last ``INSERT`` of a given query, you can pass
``last_insert_id=True`` while calling ``run_query()``, as follows::

    query = "INSERT INTO animals (name, age) VALUES ('Reglisse', 14)"
    id = mysql.run_query(query, last_insert_id=True)
    print id

This will return the last ``INSERT`` ID as an integer.

If you need to get ID of the last ``INSERT`` running a script, just add a call to 
MySQL function ``last_insert_id()`` like so::

    INSERT INTO animals (name, age) VALUES ('Reglisse', 14);
    SELECT last_insert_id() AS id;

While you run this script, this will return the ID of your last ``INSERT``::

    ({'id': 1},)

Note
====

This module is not intended to replace MySQLdb that you SHOULD use if you can
install it on the target machine.

Releases
========

- **0.4.4** (*2014-05-28*): Encoding issue fixed.
- **0.4.3** (*2014-04-03*): Project structure refactoring.
- **0.4.2** (*2014-04-03*): Fixed packaging issue.
- **0.4.1** (*2014-04-01*): Documentation fixes and added unit tests.
- **0.4.0** (*2014-04-01*): Added last_insert_id feature.
- **0.3.2** (*2014-04-01*): Project renamed from **mysql_null_driver** to
  **mysql_commando**.
- **0.3.1** (*2014-03-31*): Fixed documentation for Github and Pypi.
- **0.3.0** (*2014-03-31*): Added cast feature and unit tests.
- **0.2.0** (*2014-03-26*): Improved documentation and module refactoring
  (to move code outside __init__.py module).
- **0.1.0** (*2014-03-25*): First public release.

Enjoy!
