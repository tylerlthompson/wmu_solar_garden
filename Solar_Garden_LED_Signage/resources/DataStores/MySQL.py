"""
author: Tyler Thompson
date: October 26th 2019
"""
import pymysql
import warnings
from resources.DataStores import DataStore
from resources.config import Config


class Controller(DataStore, Config):

    def __init__(self):
        super().__init__()
        Config.__init__(self)
        self.db = None
        self.cursor = None

    def __del__(self):
        self.disconnect()

    def connection_status(self):
        if self.connect():
            self.disconnect()
            return True
        else:
            return False

    def disconnect(self):
        try:
            if self.db.open:
                self.db.close()
        except AttributeError:
            pass

    def connect(self):
        try:
            self.db = pymysql.connect(host=self.config['data_stores']['mysql']['host'],
                                      user=self.config['data_stores']['mysql']['username'],
                                      password=self.config['data_stores']['mysql']['password'],
                                      ssl=self.config['data_stores']['mysql']['ssl'] if self.config['data_stores']['mysql']['ssl_enabled'] else False,
                                      connect_timeout=self.config['data_stores']['mysql']['connect_timeout'])
            self.cursor = self.db.cursor()
            return True
        except (pymysql.err.InternalError, pymysql.err.OperationalError) as e:

            self.logger.error(msg="Failed to connect to MySQL. {0}".format(e))
            return False

    def commit(self):
        try:
            self.db.commit()
        except (pymysql.err.Error, pymysql.err.Warning) as e:
            self.logger.error(msg='Error while running committing database: {0}'.format(e))

    def query(self, query, fetch_dict=False):
        try:
            if fetch_dict:
                self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
                self.cursor.execute(query=query)
                result = self.cursor.fetchall()
                self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
                return result
            else:
                self.cursor.execute(query=query)
                try:
                    return self.cursor.fetchone()[0]
                except TypeError:
                    return self.cursor.fetchone()
        except (pymysql.err.Error, AttributeError) as e:
            self.logger.error(msg='Error while running query: {0} {1}'.format(query, e))
            return None

    def insert(self, query, data):
        with warnings.catch_warnings():
            warnings.simplefilter(self.config['warning_level'], pymysql.Warning)
            try:
                if isinstance(data, list):
                    self.cursor.executemany(query, data)
                else:
                    self.cursor.execute(query, data)
                return True
            except pymysql.err.Error as e:
                self.logger.error(msg='Error while running insert: {0} {1}'.format(query, e))
                return False
            except pymysql.err.Warning as e:
                self.logger.warn(msg='{0} {1}'.format(e, query))
                return True
