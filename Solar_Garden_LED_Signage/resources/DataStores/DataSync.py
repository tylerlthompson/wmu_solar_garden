#!/usr/bin/python3
"""
author: Tyler Thompson
date: October 26th 2019
"""
from datetime import datetime
from resources import Resource
from resources.config import Config
from resources.DataStores import MySQL


def main():
    data_sync = DataSync()
    data_sync.sync_locations()
    data_sync.sync_all_data()


class DataSync(Resource, Config):

    def __init__(self):
        super().__init__()
        Config.__init__(self)
        self.mysql = MySQL.Controller()

    def sync_all_data(self):
        """
        Download the data for all locations and save it to the config
        :return: True | False
        """
        self.read_config()
        self.mysql.connect()
        for location in self.config['data_stores']['locations']['list']:
            if self._sync_data(location=location):
                self.config['data_stores']['data_sync_time'] = str(datetime.now())
            else:
                self.mysql.disconnect()
                self.write_config()
                self.logger.error(msg="an error occurred during data sync of location {0}".format(location))
                return False
        self.mysql.disconnect()
        self.write_config()
        return True

    def _sync_data(self, location):
        """
        Download the data for a single location and save it to the config
        :param location: the name of the location as a string
        :return: True | False
        """
        dict_data = self.mysql.query(query=self.config['data_stores']['location']['query']
                                     .format(location), fetch_dict=True)
        if dict_data:
            dict_data = dict_data[0]
            for data in dict_data:
                try:
                    dict_data[data] = float(dict_data[data])
                except (TypeError, ValueError):
                    dict_data[data] = str(dict_data[data])

            self.config['data_stores']['data'][location] = dict_data
            self.logger.info(msg="data for location {0} successfully synced".format(location))
            return True
        else:
            self.logger.error(msg="Failed to connect to MySQL database.")
            return False

    def sync_locations(self):
        """
        Download the list of locations from the MySQL database and save it to the config
        :return: True | False
        """
        self.read_config()
        self.mysql.connect()
        dict_locations = self.mysql.query(query=self.config['data_stores']['locations']['query'], fetch_dict=True)
        if dict_locations:
            self.config['data_stores']['locations']['list'] = []
            for location in dict_locations:
                self.config['data_stores']['locations']['list'].append(location['name'])
            self.mysql.disconnect()
            self.write_config()
            return True
        else:
            self.logger.error(msg="Failed to connect to MySQL database.")
            return False

    def connection_status(self):
        """
        Get the status of the connection to the MySQL server
        :return: True | False
        """
        self.mysql.disconnect()
        self.mysql.connect()
        status = self.mysql.connection_status()
        self.mysql.disconnect()
        return status


if __name__ == '__main__':
    main()
