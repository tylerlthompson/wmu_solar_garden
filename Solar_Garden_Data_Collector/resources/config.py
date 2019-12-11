
config = {
    'data_stores': {
        'mysql': {
            'host': '',
            'username': '',
            'password': '',
            'warning_level': 'ignore',
            'ssl': {
                'ca': None,
                'check_hostname': False
            },
        },
    },
    'data_sources': {
        'master': {
            'http_timeout': 5,  # number of seconds to wait before a http request times out
        },
        'solar_arrays': {
            'solar_edge': {
                'master': {
                    'api_key': '',
                    'api_url': '',
                    'api_name': 'power',
                    'time_range': 60,  # how many minuets before the start time we should get the data for
                    'max_api_period': 5,  # how many days of data the api can pull at once
                    'start_time_key': '&startTime=',
                    'end_time_key': '&endTime=',
                    'time_unit': 'QUARTER_OF_AN_HOUR',  # data resolution
                    'poll_interval': 30,  # number of minuets between a request for data
                    'nested_data_key': 'values',  # the key in the raw data that contains the data
                },
                'power': {
                    'api_name': 'power',
                    'db': {
                        'name': 'SolarArray_SolarEdge_Power',
                        'update_statement': 'call SolarGarden.SolarArray_SolarEdge_UpdatePower(%s, %s);',
                    },
                },
                'energy': {
                    'api_name': 'energy',
                    'start_time_key': '&startDate=',
                    'end_time_key': '&endDate=',
                    'db': {
                        'name': 'SolarArray_SolarEdge_Energy',
                        'update_statement': 'call SolarGarden.SolarArray_SolarEdge_UpdateEnergy(%s, %s);',
                    },
                },
                'overview': {
                    'api_name': 'overview',
                    'poll_interval': 1440,
                    'db': {
                        'name': 'SolarArray_SolarEdge_Overview',
                        'update_statement': 'call SolarGarden.SolarArray_SolarEdge_UpdateOverview(%s, %s, %s, %s, %s);',
                    },
                },
                'inverter': {
                    'api_name': 'data',
                    'api_url': '',
                    'nested_data_key': 'telemetries',
                    'db': {
                        'name': 'SolarArray_SolarEdge_Inverter',
                        'update_statement': 'call SolarGarden.SolarArray_SolarEdge_UpdateInverter(%s, %s, %s, %s, %s, '
                                            '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);',
                    },
                },
            },
            'sma': {

            },
        },
        'weather_stations': {
            'master': {
                'records_key': '&records=',
                'max_api_period': 14,  # how many days of data the api can pull at once
            },
            'floyd_hall': {
                'url': '',
                'poll_interval': 10,
                'db': {
                    'name': 'WeatherStation_FloydHall',
                    'update_statement': 'call SolarGarden.WeatherStation_FloydHall_Update(%s, %s, %s, %s, %s, %s, %s, '
                                        '%s, %s, %s);',
                },
            },
            'wood_hall': {
                'url': '',
                'poll_interval': 60,
                'db': {
                    'name': 'WeatherStation_WoodHall',
                    'update_statement': 'call SolarGarden.WeatherStation_WoodHall_Update(%s, %s, %s, %s, %s);',
                },
            },
        },
    },
}

