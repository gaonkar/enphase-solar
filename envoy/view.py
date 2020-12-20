import time
import os
import sys
import datetime as dt
import configparser
import argparse
import json
import requests
import pprint
import pystore
import pandas as pd

#import from common folder
curFileP = os.path.dirname(os.path.realpath(__file__))
commonWP = os.path.join(curFileP, "../common")
sys.path.insert(0, commonWP)
import utils
from logconfig import LogConfig

class View:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.data_path = config['DEFAULT']['data_path']
        pystore.set_path(self.data_path)
        self.store = pystore.store(config['DEFAULT']['data_store'])
        self.collectionName = config['DEFAULT']['collections']
        self.items = config['DEFAULT']['items'].split(',')
        #create collections
        self.collection = self.store.collection(self.collectionName)

    def get_df(self, table):
        table = self.collection.item(table)
        return table.to_pandas()

# main() will be executed
if __name__ == '__main__':

    startTime = dt.datetime.now()
    config = configparser.ConfigParser()
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--configDir', help='path to config directory',
                        default="./config")
    args = parser.parse_args()
    baseName = os.path.basename(__file__)
    # read the configuration file
    config = utils.GetConfigFromFilePath(args.configDir, baseName)

    # Get the logger setup
    logConfig = LogConfig(args.configDir, config, baseName)
    logger = logConfig.ConfigLog(config['LOGGING']['logType'])
    # setup access to pystore
    view = View(logger, config)
    prod = view.get_df("production")
    print(prod)
