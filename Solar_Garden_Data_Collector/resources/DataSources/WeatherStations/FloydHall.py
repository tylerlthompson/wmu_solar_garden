
from resources.DataSources.WeatherStations import WeatherStation
from resources.config import config


class FloydHall(WeatherStation):

    def __init__(self):
        super().__init__()
        self.config = config['data_sources']['weather_stations']['floyd_hall']

    def format_raw_data(self, raw_data):
        try:
            formatted_data = []
            for data in raw_data:
                formatted_data.append((data['TimeStamp'], data['AirTempC'], data['Rain_in_Tot'], data['WindDir'],
                                       data['WS_ms'], data['DewPtC'], data['SlrkW'], data['SlrMJ_Tot'],
                                       data['Raw_mV'], data['RH']))
            return formatted_data
        except (KeyError, TypeError) as e:
            self.logger.error(msg="Failed to format raw data. {0}".format(e))
            return None
