from resources import Resource
from resources.config import config
from abc import abstractmethod


class DataSource(Resource):

    def __init__(self):
        super().__init__()
        self.__config = config['data_sources']['master']

    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, value):
        x = dict(self.config)
        x.update(value)
        self.__config = x

    @abstractmethod
    def get_raw_data(self, start_time, end_time):
        self.logger.error(msg=self.__not_implemented_error__)
        raise NotImplementedError(self.__not_implemented_error__)

    @abstractmethod
    def format_raw_data(self, raw_data):
        self.logger.error(msg=self.__not_implemented_error__)
        raise NotImplementedError(self.__not_implemented_error__)
