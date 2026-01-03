#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import logging

class Logger:

    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def set_level(self, loglevel):
        match loglevel:
            case 'debug':
                level = logging.DEBUG
            case 'error':
                level = logging.ERROR
            case 'info':
                level = logging.INFO
            case 'warning':
                level = logging.WARNING
            case _:
                level = logging.NOTSET

        self.logger.setLevel(level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        formatter = logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s:%(message)s')
        console_handler.setFormatter(formatter)

        # Add the console handler only if there are no handlers already
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)

    def set_filename(self, filename):

        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s,%(levelname)s,%(name)s,%(message)s')
        file_handler.setFormatter(formatter)

        # Add the console handler only if there are no handlers already
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
    
    def critical(self, message):
        self.logger.critical(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)

    # def check_difference(function_name, difference):
    #     if difference > 1:
    #         Logger.warning(message)


class Message:


    def printer(text):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print('{} {}'.format(current_time, text), end='\r')
