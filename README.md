mysql_null_driver
=================

MySQL driver that calls database on command line so that you don't have to
install any library to run you favorite Python script on this old server where
you can't install anything.

To use this library, drop its module (that is the file _mysql_null_driver.py_)
in your source directory and use it like this:

```python
from mysql_null_driver import MysqlNullDriver

mysql = MysqlNullDriver(hostname='localhost', database='test',
                        username='test', password='test')     
result = mysql.run_query("SHOW DATABASES")
print result
```

When query returns nothing (after an _INSERT_ for instance), method
_run_query()_ will return _None_. If query returns a result set, this will be
a tuple of dictionaries. For instance, previous sample code would print:

```python
({'Database': 'information_schema'}, {'Database': 'mysql'}, {'Database': 'test'})
```

This module is not intended to replace MySQLdb that you SHOULD use if you can
install it on the target machine.

Enjoy!