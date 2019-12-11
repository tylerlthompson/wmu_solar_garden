
from resources.DataSources.WeatherStations import WeatherStation
from resources.config import config


class WoodHall(WeatherStation):

    def __init__(self):
        super().__init__()
        self.config = config['data_sources']['weather_stations']['wood_hall']

    def format_raw_data(self, raw_data):
        try:
            formatted_data = []
            for data in raw_data:
                formatted_data.append((data['TimeStamp'], data['AirTC'], data['Rain_mm_Tot'], data['WindDir'],
                                       data['WS_ms']))
            return formatted_data
        except (KeyError, TypeError) as e:
            self.logger.error(msg="Failed to format raw data. {0}".format(e))
            return None
