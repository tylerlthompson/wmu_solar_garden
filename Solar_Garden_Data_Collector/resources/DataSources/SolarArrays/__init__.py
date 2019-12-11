from abc import abstractmethod
from resources.DataSources import DataSource


class SolarArray(DataSource):

    @abstractmethod
    def get_raw_data(self, start_time, end_time):
        self.logger.error(msg=self.__not_implemented_error__)
        raise NotImplementedError(self.__not_implemented_error__)

    @abstractmethod
    def format_raw_data(self, raw_data):
        self.logger.error(msg=self.__not_implemented_error__)
        raise NotImplementedError(self.__not_implemented_error__)
