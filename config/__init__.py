import pymysql
from django.db.backends.base.base import BaseDatabaseWrapper

# Django 6 requires mysqlclient >= 2.2.1; patch PyMySQL version to satisfy the check.
pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.__version__ = "2.2.1"
pymysql.install_as_MySQLdb()

# Bypass MariaDB version check for local development (XAMPP MariaDB 10.4)
BaseDatabaseWrapper.check_database_version_supported = lambda self: None

# MariaDB < 10.5 does not support INSERT ... RETURNING
from django.db.backends.mysql.features import DatabaseFeatures
DatabaseFeatures.can_return_columns_from_insert = property(
    lambda self: self.connection.mysql_is_mariadb and self.connection.mysql_version >= (10, 5, 0)
)


