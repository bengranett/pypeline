# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
from config import Config, Defaults

logging.basicConfig(level=logging.INFO)


class pype(object):

    def __init__(self, config={}, **args):
        """ Initialize pypelid class"""

        self._parse_config(config, **args)

        self._setup_logging()

    def _setup_logging(self):
        """ Initialize a local logger"""
        name = type(self).__name__
        self.logger = logging.getLogger(name)

        if self.config['verbose'] == 0:
            level = logging.CRITICAL
        elif self.config['verbose'] == 1:
            level = logging.INFO
        else:
            level = logging.DEBUG

        self.logger.setLevel(level)
        self.logger.debug("set up logger %s", type(self).__name__)

    def _parse_config(self, config={}, **args):
        """ Parse input config dictionary"""
        self.config = config

        # merge key,value arguments and config dict
        for key, value in args.items():
            self.config[key] = value

        # Add any parameters that are missing
        for key, def_value in self._default_params.items():
            try:
                self.config[key]
            except KeyError:
                self.config[key] = def_value


def add_param(*args, **kwargs):
    """ Add a config parameter """
    def wrap(cls):
        try:
            getattr(cls, '_default_params')
        except AttributeError:
            cls._default_params = Defaults()

        cls._default_params.add_param(*args, **kwargs)
        return cls
    return wrap


def depends_on(*args):
    """ Add a class dependency """
    def wrap(cls):
        try:
            getattr(cls, '_dependencies')
        except AttributeError:
            cls._dependencies = []
        for a in args:
            cls._dependencies.append(a)
        return cls
    return wrap
