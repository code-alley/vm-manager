
import configparser
from os import path


class Config:

    def __init__(self):
        self.config = None
        self.section = None

    def load(self, cfg_file, section):
        if not path.exists(cfg_file):
            raise FileNotFoundError()
        self.config = configparser.ConfigParser()
        self.config.read(cfg_file)
        self.section = section

    def get(self, name):
        return self.config[self.section][name]
