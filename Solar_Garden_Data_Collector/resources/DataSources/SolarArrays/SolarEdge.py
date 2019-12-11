
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from resources.DataSources.SolarArrays import SolarArray
from resources.config import config


class Controller(SolarArray):

    def __init__(self):
        super().__init__()
        self.config = config['data_sources']['solar_arrays']['solar_edge']['master']

    def get_raw_data(self, start_time=datetime.now(), end_time=False):
        """
        :param start_time:
        :param end_time:
        :return:
        """
        if not start_time:
            start_time = datetime.now()
        if not end_time:
            end_time = datetime.now()

        # set time format
        if 'Date' in self.config['start_time_key']:
            time_format = '%Y-%m-%d'
        else:
            time_format = '%Y-%m-%d %H:%M:00'

        # set start and end times/dates
        start_time_str = (start_time - timedelta(minutes=self.config['time_range'])).strftime(time_format)
        end_time_str = end_time.strftime(time_format)

        print(start_time_str, end_time_str)

        # make the API request
        try:
            r = requests.get(url='{0}/{1}.json?api_key={2}{3}{4}{5}{6}&timeUnit={7}'.
                             format(self.config['api_url'],  self.config['api_name'], self.config['api_key'],
                                    self.config['start_time_key'], start_time_str, self.config['end_time_key'],
                                    end_time_str, self.config['time_unit']),
                             timeout=self.config['http_timeout'])

        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout) as e:
            self.logger.error(msg="Failed to connect to SolarEdge API. {0}".format(e))
            return

        # handle return codes
        if r.status_code == 200:
            self.logger.info(msg="Successfully pulled raw data from SolarEdge API {0}".format(self.config['api_name']))
            return r.json()

        elif r.status_code == 400:
            error_message = BeautifulSoup(r.content, 'html.parser').find_all('u')
            self.logger.error(msg="Data was not sent correctly to the SolarEdge API {0} {1}".format(r.url,
                                                                                                    error_message))
            return

        # requested time frame exceed
        elif r.status_code == 403:
            error_message = BeautifulSoup(r.content, 'html.parser').find_all('u')
            self.logger.error(msg="The requested time frame exceeds the SolarEdge API limit. "
                                  "Attempting incremental update... {0} {1}".format(r.url, error_message))

            return self._get_raw_data_incrementally(start_time=start_time, end_time=end_time)

        else:
            self.logger.error(msg="Failed to contact SolarEdge. "
                                  "Server returned bad status code. {0} {1} {2}".format(r.url, r.status_code, r.text))
            return

    def format_raw_data(self, raw_data):
        try:
            formatted_data = []
            data_list = raw_data[self.config['api_name']]['values']
            for data in data_list:
                if not data['value']:
                    data['value'] = 0.0
                formatted_data.append((data['date'], data['value']))
            return formatted_data
        except (KeyError, TypeError) as e:
            self.logger.error(msg="Failed to format raw data. {0}".format(e))
            return None

    def _get_raw_data_incrementally(self, start_time, end_time):

        days_behind = (datetime.now() - start_time).days
        number_of_runs = int(days_behind / self.config['max_api_period']) - 1
        inc_end_time = start_time + timedelta(days=self.config['max_api_period'])
        return_data = self.get_raw_data(start_time=start_time, end_time=inc_end_time)

        for _ in range(number_of_runs):
            start_time = inc_end_time
            inc_end_time = inc_end_time + timedelta(days=self.config['max_api_period'])

            if inc_end_time > end_time:
                inc_end_time = datetime.now()

            next_data = self.get_raw_data(start_time=start_time, end_time=inc_end_time)

            for data in next_data[self.config['api_name']][self.config['nested_data_key']]:
                return_data[self.config['api_name']][self.config['nested_data_key']].append(data)

        return return_data


class Power(Controller):

    def __init__(self):
        super().__init__()
        self.config = config['data_sources']['solar_arrays']['solar_edge']['power']


class Energy(Controller):

    def __init__(self):
        super().__init__()
        self.config = config['data_sources']['solar_arrays']['solar_edge']['energy']


class Overview(Controller):

    def __init__(self):
        super().__init__()
        self.config = config['data_sources']['solar_arrays']['solar_edge']['overview']

    def format_raw_data(self, raw_data):
        try:
            data = raw_data[self.config['api_name']]
            return ((data['lastUpdateTime'], data['lifeTimeData']['energy'], data['lastYearData']['energy'],
                     data['lastMonthData']['energy'], data['lastDayData']['energy']))
        except (KeyError, TypeError) as e:
            self.logger.error(msg="Failed to format raw data. {0}".format(e))
            return None


class Inverter(Controller):

    def __init__(self):
        super().__init__()
        self.config = config['data_sources']['solar_arrays']['solar_edge']['inverter']

    def format_raw_data(self, raw_data):
        try:
            data_list = raw_data[self.config['api_name']]['telemetries']
            formatted_data = []
            for data in data_list:
                formatted_data.append((data['date'], data['totalActivePower'], data['dcVoltage'],
                                       data['groundFaultResistance'], data['powerLimit'], data['temperature'],
                                       data['inverterMode'], data['operationMode'], data['L1Data']['acCurrent'],
                                       data['L1Data']['acVoltage'], data['L1Data']['acFrequency'],
                                       data['L1Data']['apparentPower'], data['L1Data']['activePower'],
                                       data['L1Data']['reactivePower'], data['L1Data']['cosPhi']))
            return formatted_data
        except (KeyError, TypeError) as e:
            self.logger.error(msg="Failed to format raw data. {0}".format(e))
            return None
