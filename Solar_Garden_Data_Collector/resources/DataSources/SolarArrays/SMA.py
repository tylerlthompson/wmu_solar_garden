
from resources.DataSources.SolarArrays import SolarArray
from resources.config import config


class Controller(SolarArray):

    def __init__(self):
        super().__init__()
        self.config.update(config['data_sources']['solar_arrays']['sma'])

