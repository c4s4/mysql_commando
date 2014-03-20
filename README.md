mysql_null_driver
=================

MySQL driver that calls database on command line so that you don't have to
install any library to run you favorite Python script on this old server where
you can't install anything.

To use this library, drop its module (that is the file _mysql_null_driver.py_)
in your source directory and use it like this:

```python
import mysql_null_driver

mysql = mysql_null_driver.MysqlNullDriver()
result = mysql.run_query("SHOW DATABASES")
print result
```


