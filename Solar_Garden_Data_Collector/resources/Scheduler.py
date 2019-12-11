from datetime import datetime
from resources.DataStores import MySQL
from resources import Resource


class Scheduler(Resource):

    def __init__(self):
        super().__init__()
        self.scheduled_objects = []
        self.mysql = MySQL.Controller()

    def run_schedule(self):
        if self.scheduled_objects:
            for scheduled_object in self.scheduled_objects:
                if self.check_schedule_time(scheduled_object=scheduled_object):
                    self.mysql.connect()
                    self.execute_object(scheduled_object=scheduled_object)
                    self.mysql.commit()
                    self.mysql.disconnect()

    @staticmethod
    def check_schedule_time(scheduled_object):
        object_name = type(scheduled_object).__name__
        now = datetime.now().replace(second=0, microsecond=0)
        minuets_from = int((now - now.replace(hour=0, minute=0, second=0, microsecond=0))
                           .total_seconds() / 60) % scheduled_object.config['poll_interval']
        minuets_until = scheduled_object.config['poll_interval'] - minuets_from
        # print('{0} will run in {1} minute(s)'.format(object_name, minuets_until))
        if minuets_from == 0:
            return True
        else:
            return False

    def execute_all_objects(self):
        self.mysql.connect()
        for scheduled_object in self.scheduled_objects:
            self.execute_object(scheduled_object=scheduled_object)
        self.mysql.commit()
        self.mysql.disconnect()

    def execute_object(self, scheduled_object):
        object_name = type(scheduled_object).__name__
        # retrieve start time for data query
        start_time = self.mysql.query(query="call SolarGarden.LatestDatetime('{0}')"
                                      .format(scheduled_object.config['db']['name']))

        # pull the raw data from the DataSource
        raw_data = scheduled_object.get_raw_data(start_time=start_time)
        # print(raw_data)
        if not raw_data:
            self.logger.error(msg="Received empty raw data from DataSource {0}".format(object_name))
            return

        # format the raw data of the DataSource for the data base
        data = scheduled_object.format_raw_data(raw_data=raw_data)
        if not data:
            self.logger.error(msg="Received empty formatted data from DataSource {0}".format(object_name))
            return

        # update the database with new data pulled from the DataSource
        if self.mysql.insert(query=scheduled_object.config['db']['update_statement'], data=data):
            self.logger.info(msg="Successfully updated database for DataSource {0}".format(object_name))
        else:
            self.logger.error(msg="Failed to update database for DataSource {0}".format(object_name))

    def add_object(self, schedule_object):
        self.scheduled_objects.append(schedule_object)
