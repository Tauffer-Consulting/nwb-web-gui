import configparser
import os


class Config:
    """Base config."""
    # SECRET_KEY = 'SECRET_KEY'
    SESSION_COOKIE_NAME = 'SESSION_COOKIE_NAME'
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SEND_FILE_MAX_AGE_DEFAULT = 0

    NWB_CONVERTER_CLASS = 'example'  # default example converter


class ConfigProduction(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'DATABASE_URI_PRODUCTION'


class ConfigDev(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    DATABASE_URI = 'DEV_DATABASE_URI'

    # DATA_PATH = '/home/vinicius/Área de Trabalho/Trabalhos/nwb-web-gui/files'
    # DATA_PATH = r'C:\Users\Luiz\Desktop\data_app'

    # The following variables are recovered by the app from ENV variables
    # In Development, we get them from a .ini file and set the ENV vars
    # In production, these ENV vars should be set in other ways
    parser = configparser.ConfigParser()
    parser.read('config.ini')

    if 'DATA' in parser.sections():
        os.environ['DATA_PATH'] = parser['DATA']['DATA_PATH']

    if 'NWB_CONVERTER' in parser.sections():
        os.environ['NWB_CONVERTER_MODULE'] = parser['NWB_CONVERTER']['NWB_CONVERTER_MODULE']
        os.environ['NWB_CONVERTER_CLASS'] = parser['NWB_CONVERTER']['NWB_CONVERTER_CLASS']

    if 'NWB_DASHBOARD' in parser.sections():
        os.environ['NWB_DASHBOARD_MODULE'] = parser['NWB_DASHBOARD']['NWB_DASHBOARD_MODULE']
        os.environ['NWB_DASHBOARD_CLASS'] = parser['NWB_DASHBOARD']['NWB_DASHBOARD_CLASS']

    if 'SECRETS' in parser.sections():
        os.environ['SECRET_KEY'] = parser['SECRETS']['SECRET_KEY']
