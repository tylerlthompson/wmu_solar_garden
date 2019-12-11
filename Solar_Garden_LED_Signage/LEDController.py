#!/usr/bin/python3
"""
author: Tyler Thompson
date: October 26th 2019
"""
import netifaces
import datetime
from time import sleep
from resources.Displays import Frames
from resources.Displays.LEDMatrix import LEDMatrix
from resources.config import Config
from resources.DataStores.DataSync import DataSync
from resources import logging

logger = logging.get_logger(__name__)


def main():
    data_sync = DataSync()
    config = Config()
    display = LEDMatrix()

    show_network_status(display=display,
                        show_time_seconds=config.config['displays']['led_matrix']['net_info_show_seconds'])

    while True:
        config.read_config()
        display.update_brightness()
        sql_con = data_sync.connection_status()
        if sql_con:
            data_sync.sync_all_data()
        else:
            logger.error(msg="Failed to contact database, data map frames will be disabled.")

        frames = get_frames(config=config.config, display=display, generate_maps=sql_con)
        for frame in frames:
            frame.show()
            sleep(frame.duration)


def show_network_status(display, show_time_seconds):
    """
    Show the network status on the display
    :param display: a LEDMatrix object
    :param show_time_seconds: number of seconds to show network info
    :return: None
    """
    font = "6x9"
    try:
        display.show_text(text="LAN: {0}".format(netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']), font=font)
    except KeyError:
        display.show_text(text="LAN: Not Connected", font=font)
    display.show_text(text="{0}".format(netifaces.ifaddresses('eth0')[netifaces.AF_LINK][0]['addr']), y=18, font=font)
    try:
        display.show_text(text="WiFi: {0}".format(netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']), y=36, font=font)
    except KeyError:
        display.show_text(text="WiFi: Not Connected", y=36, font=font)
    display.show_text(text="{0}".format(netifaces.ifaddresses('wlan0')[netifaces.AF_LINK][0]['addr']), y=45, font=font)
    sleep(show_time_seconds)


def get_frames(config, display, generate_maps):
    """
    Get a list of Frames to display
    :param config: the main config as a dictionary
    :param display: a LEDMatrix object
    :param generate_maps: True - data maps are generated | False - data maps are not generated
    :return: a list of Frame objects
    """
    if generate_maps:
        # enable/disable locations based of freshness of data
        today = datetime.datetime.today()
        margin = datetime.timedelta(hours=config['data_stores']['data_freshness_threshold_hours'])
        for location in config['data_stores']['data']:
            collection_datetime = datetime.datetime.strptime(config['data_stores']['data'][location]['collection_datetime'], '%Y-%m-%d %H:%M:%S')
            if today - margin >= collection_datetime:
                config['data_stores']['data'][location]['enabled'] = False
                logger.error("Collection datetime for location {0} if out of freshness threshold {1} hours. Data maps for that location will be disabled. {2}".format(location, config['data_stores']['data_freshness_threshold_hours'], config['data_stores']['data'][location]['collection_datetime']))
            else:
                config['data_stores']['data'][location]['enabled'] = True

    frames = []
    for frame in config['frames']:
        if frame['enabled']:
            # generate non data maps frames
            if "data" not in frame['type']:
                frames.append(Frames.create_frame(display=display, config=frame))
                logger.debug(msg="Generating Frame: {0} Type: {1}".format(frame['description'], frame['type']))
            elif generate_maps:
                # generate data map frames, if sql connection and data is fresh
                if config['data_stores']['data'][frame['location']]['enabled']:
                    frames.append(Frames.create_frame(display=display, config=frame))
                    logger.debug(msg="Generating Frame: {0} Type: {1}".format(frame['description'], frame['type']))
    frames = sorted(frames, key=lambda x: x.order)
    return frames


if __name__ == '__main__':
    main()
