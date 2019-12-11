"""
author: Tyler Thompson
date: October 26th 2019
"""
from git import *
import time, json, os
from resources import logging


class Config:

    def __init__(self):
        self.logger = logging.get_logger(__name__)
        self.__program_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.__config_file = '{0}/resources/config.json'.format(self.__program_dir)
        self.image_dir = '{0}/images'.format(self.__program_dir)
        self.__font_dir = '{0}/matrix/fonts'.format(self.__program_dir)
        self.log_dir = "{0}/resources/logs".format(self.__program_dir)
        self.__config = {}
        self.read_config()

    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, value):
        x = self.__config
        x.update(value)
        self.__config = x

    def write_config(self):
        with open(self.__config_file, 'w') as json_file:
            json_file.write(json.dumps(self.config, indent=4, sort_keys=False))

    def read_config(self):
        with open(self.__config_file) as json_file:
            self.__config = json.load(json_file)
        return self.config

    def __update_frame_indexes(self):
        i = 0
        for frame in self.__config['frames']:
            frame['index'] = i
            i += 1

    def __validate_value_type(self, frame_type, key, value):
        if self.config['frame_templates'][frame_type][key] == 'int':
            try:
                return int(value)
            except ValueError:
                return 0
        elif self.config['frame_templates'][frame_type][key] == 'bool':
            return True if str(value) == 'on' else False
        else:
            return value

    def font_to_file_path(self, font):
        return "{0}/{1}.bdf".format(self.__font_dir, font)

    @staticmethod
    def font_to_x_y(font):
        ret = str(font).replace('B', '').replace('O', '').split('x')
        ret = [int(ret[0]), int(ret[1])]
        return ret

    @staticmethod
    def hex_to_rgb(color):
        color = color.replace('#', '')
        return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))

    def add_frame(self, new_config):
        new_frame = {}
        for key in self.config['frame_templates'][new_config['type']]:
            new_frame[key] = self.__validate_value_type(frame_type=new_config['type'], key=key, value=new_config[key])
        self.config['frames'].append(new_frame)
        self.__update_frame_indexes()
        self.logger.info(msg="new frame created: {0}".format(new_frame))
        self.write_config()
        self.read_config()
        return self.config

    def del_frame(self, frame_index):
        self.logger.info(msg="deleting frame: {0}".format(self.__config['frames'][frame_index]))
        try:
            if self.__config['frames'][frame_index]['type'] == 'image':
                os.remove(os.path.join(self.image_dir, self.__config['frames'][frame_index]['image']))
        except OSError:
            pass
        del self.__config['frames'][frame_index]
        self.__update_frame_indexes()
        self.write_config()
        self.read_config()
        return self.config

    def update_frame(self, frame):
        for setting in frame:
            try:
                frame[setting] = self.__validate_value_type(frame_type=frame['type'], key=setting, value=frame[setting])
            except ValueError:
                self.logger.info(msg="User input failed to validate {0} {1}".format(setting, frame[setting]))
                return False
        self.config['frames'][frame['index']] = frame
        # self.__update_frame_indexes()
        self.logger.info(msg="frame has been updated: {0}".format(frame))
        self.write_config()
        self.read_config()
        return True


class Git(object):

    def __init__(self):
        self.repoRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.repo = Repo(self.repoRoot, odbt=GitDB)
        self.branch = self.repo.active_branch
        self.remote = self.repo.remotes.origin.url
        self.author = self.repo.head.commit.author
        self.authorContact = self.repo.head.commit.committer.email
        self.description = self.repo.description
        self.commit = self.repo.heads.master.commit
        self.lastCommittedDate = time.asctime(time.gmtime(self.repo.heads.master.commit.committed_date))
