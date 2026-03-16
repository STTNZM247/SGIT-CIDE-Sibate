import pymysql

# Django 6 requires mysqlclient >= 2.2.1; patch PyMySQL version to satisfy the check.
pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.__version__ = "2.2.1"
pymysql.install_as_MySQLdb()
