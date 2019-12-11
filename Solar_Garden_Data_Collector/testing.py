
from time import sleep
from resources.DataSources.WeatherStations import WoodHall, FloydHall
from resources.DataSources.SolarArrays import SolarEdge
from resources.DataStores import MySQL
from datetime import datetime


def main():
    mysql = MySQL.Controller()
    mysql.connect()

    wood_start_time = mysql.query(query="call SolarGarden.LatestDatetime('WeatherStation_WoodHall');")
    print(wood_start_time)

    raw_wood_data = WoodHall.WoodHall().get_raw_data(start_time=wood_start_time)
    print(raw_wood_data)

    wood_data = WoodHall.WoodHall().format_raw_data(raw_data=raw_wood_data)
    print(wood_data)

    mysql.insert_list(query="call SolarGarden.WeatherStation_WoodHall_Update(%s, %s, %s, %s, %s);",
                      data=wood_data)

    # floyd_start_time = mysql.query(query="call SolarGarden.LatestDatetime('WeatherStation_FloydHall');")
    # print(floyd_start_time)
    #
    # raw_floyd_data = FloydHall.Controller().get_raw_data(start_time=floyd_start_time)
    # print(raw_floyd_data)
    #
    # floyd_data = FloydHall.Controller().format_raw_data(raw_data=raw_floyd_data)
    # print(floyd_data)
    #
    # mysql.insert_list(query="call SolarGarden.WeatherStation_FloydHall_Update(%s, %s, %s, %s, %s, %s);", insert_list=floyd_data)

    # power_start_time = mysql.query(query="call SolarGarden.LatestDatetime('SolarArray_SolarEdge_Power');")
    # energy_start_time = mysql.query(query="call SolarGarden.LatestDatetime('SolarArray_SolarEdge_Energy');")
    # inverter_start_time = mysql.query(query="call SolarGarden.LatestDatetime('SolarArray_SolarEdge_Inverter');")
    # print(power_start_time, energy_start_time, inverter_start_time)
    # print()
    #
    # raw_power_data = SolarEdge.Power().get_raw_data(start_time=power_start_time)
    # raw_energy_data = SolarEdge.Energy().get_raw_data(start_time=energy_start_time)
    # raw_inverter_data = SolarEdge.Inverter().get_raw_data(start_time=inverter_start_time)
    #
    # print(raw_power_data)
    # print(raw_energy_data)
    # print(raw_inverter_data)
    # print()
    #
    # power_data = SolarEdge.Power().format_raw_data(raw_data=raw_power_data)
    # energy_data = SolarEdge.Energy().format_raw_data(raw_data=raw_energy_data)
    # inverter_data = SolarEdge.Inverter().format_raw_data(raw_data=raw_inverter_data)
    #
    # print(power_data)
    # print(energy_data)
    # print(inverter_data)
    # print()
    #
    # mysql.insert_list(query="call SolarGarden.SolarArray_SolarEdge_UpdatePower(%s, %s);", insert_list=power_data)
    # mysql.insert_list(query="call SolarGarden.SolarArray_SolarEdge_UpdateEnergy(%s, %s);", insert_list=energy_data)
    # mysql.insert_list(query="call SolarGarden.SolarArray_SolarEdge_UpdateInverter(%s, %s, %s, %s, %s, %s, %s, %s, %s,"
    #                         " %s, %s, %s, %s, %s, %s);",
    #                   insert_list=inverter_data)
    #
    # raw_overview_data = SolarEdge.Overview().get_raw_data()
    # print(raw_overview_data)
    #
    # overview_data = SolarEdge.Overview().format_raw_data(raw_data=raw_overview_data)
    # print(overview_data)
    #
    # mysql.insert(query="call SolarGarden.SolarArray_SolarEdge_UpdateOverview(%s, %s, %s, %s, %s);",
    #              data=overview_data)

    mysql.commit()
    mysql.disconnect()


if __name__ == '__main__':
    main()
