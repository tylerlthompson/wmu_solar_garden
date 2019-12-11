#!/usr/bin/python3
from time import sleep
from resources.DataSources.SolarArrays import SolarEdge
from resources.DataSources.WeatherStations import FloydHall, WoodHall
from resources.Scheduler import Scheduler


def main():
    scheduler = Scheduler()
    scheduler.add_object(schedule_object=SolarEdge.Power())
    scheduler.add_object(schedule_object=SolarEdge.Energy())
    scheduler.add_object(schedule_object=SolarEdge.Inverter())
    scheduler.add_object(schedule_object=FloydHall.FloydHall())
    scheduler.add_object(schedule_object=WoodHall.WoodHall())
    scheduler.add_object(schedule_object=SolarEdge.Overview())

    scheduler.execute_all_objects()

    while True:
        scheduler.run_schedule()
        sleep(59)


if __name__ == '__main__':
    main()
