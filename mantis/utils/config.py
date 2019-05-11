import configparser

from mantis.utils import path as _path


class Config:
    def __init__(self, path=_path.resolve('./config.ini')):
        config = configparser.ConfigParser()
        config.read(path)
        self.database = config['Database']
