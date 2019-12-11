
from resources import logging
from abc import ABCMeta  # , abstractmethod


class Resource:
    __metaclass__ = ABCMeta
    __not_implemented_error__ = "function has not been implemented in the subclass."

    def __init__(self):
        # Initialize logging with the standard/basic logger.
        self.logger = logging.get_logger(__name__)
