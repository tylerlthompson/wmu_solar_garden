
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from abc import abstractmethod
from resources.DataSources import DataSource
from resources.config import config


class WeatherStation(DataSource):

    def __init__(self):
        super().__init__()
        self.config.update(config['data_sources']['weather_stations']['master'])

    def get_raw_data(self, start_time=datetime.now(), end_time=datetime.now()):
        # calculate how many records to pull
        records = int((divmod((end_time - start_time).total_seconds(), 60)[0]) / self.config['poll_interval'])
        if records <= 0:
            records = 1

        # attempt to connect to server
        try:
            r = requests.get(url='{0}{1}{2}'.format(self.config['url'], self.config['records_key'], records),
                             timeout=self.config['http_timeout'])
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout) as e:
            self.logger.error(msg="Failed to connect to weather station, url: {0} {1}".format(self.config['url'], e))
            return None

        # check response code of server
        if r.status_code != 200:
            self.logger.error(msg="Failed to get any data from weather station, url: {0}".format(self.config['url']))
            return None

        # parse out raw data
        soup = BeautifulSoup(r.content, 'html.parser')
        data_list = []
        headers = []
        for th in soup.select('th'):
            headers.append(th.text.strip())

        for tr in soup.select('tr'):
            data = {}
            for i, td in enumerate(tr.select('td')):
                data[headers[i]] = td.text.strip()
            if data:
                data_list.append(data)
        self.logger.info(msg="Successfully pulled raw data from Weather Station {0}".format(type(self).__name__))
        return data_list

    @abstractmethod
    def format_raw_data(self, raw_data):
        self.logger.error(msg=self.__not_implemented_error__)
        raise NotImplementedError(self.__not_implemented_error__)
