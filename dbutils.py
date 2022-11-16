# -*- encoding: utf-8 -*-
# @auther  : wangzs
# @time    : 2022-11-06
# @file    : dbutils.py
# @function: 数据库操作
import logging
import cfg
import pymysql
import pymongo

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')


class MysqlUtil:
    def __init__(self):
        self._db_host = cfg.MYSQL_HOST
        self._db_user = cfg.MYSQL_USER
        self._db_pswd = cfg.MYSQL_PASSWD
        self._db_port = cfg.MYSQL_PORT
        self._db_name = cfg.MYSQL_DBNAME
        self._conn = None

    def _connect(self):
        """
        建立数据库连接
        :return:
        """
        self._conn = pymysql.connect(host=self._db_host,
                                     user=self._db_user,
                                     password=self._db_pswd,
                                     port=self._db_port,
                                     db=self._db_name)

    def _close(self):
        """
        关闭数据库连接
        :return:
        """
        self._conn.close()

    def exec_sql(self, op: str, table: str, data: dict):
        """
        执行sql操作
        :param op: 操作类型
        :param table: 表
        :param data: 数据（字典）
        :return:
        """
        self._connect()
        cursor = self._conn.cursor()
        if op == 'query':  # 查询操作
            columns = data.get('columns')
            condition = data.get('condition')
            sql = 'SELECT {columns} FROM {table} WHERE {query_condition}'.format(columns=columns, table=table,
                                                                                 query_condition=condition)
            try:
                cursor.execute(sql)
                logging.info('执行查询成功：%s', sql)
                return cursor.fetchall()
            except:
                logging.error('执行查询失败：%s', sql)
                return False
        elif op == 'insert':  # 插入操作
            keys = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))  # ['%s', '%s', '%s'] -> '%s, %s, %s'
            sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
            try:
                if cursor.execute(sql, tuple(data.values())):
                    logging.info('数据插入成功：%s', sql % tuple(data.values()))
                    self._conn.commit()
                    return True
            except:
                logging.error('数据插入失败：%s', sql % tuple(data.values()))
                return False
        self._close()


class MongodbUtil:
    pass
