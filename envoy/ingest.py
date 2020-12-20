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

class Ingest:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.url = config['DEFAULT']['url']
        self.username=config['DEFAULT']['user']
        self.data_path = config['DEFAULT']['data_path']
        self.now = dt.date.today().strftime("%Y-%m-%d")
        self.logger.debug(self.now)
        pystore.set_path(self.data_path)
        self.store = pystore.store(config['DEFAULT']['data_store'])
        self.collectionName = config['DEFAULT']['collections']
        self.items = config['DEFAULT']['items'].split(',')
        #create collections
        self.collection = self.store.collection(self.collectionName)
 
    def get_http_plain(self, urlpath):
        from base64 import b64encode
        url = os.path.join(self.url, urlpath)
        self.logger.debug("Fetching plaintext data from " + url)
        try:
            res = requests.get(url)
            return res.json()

        except Exception as e:
            self.logger.erro("get_data failure" + str(e))
            return None

           
    def get_http_basicauth(self, urlpath):
        from base64 import b64encode
        url = os.path.join(self.url, urlpath)
        #headers = { 'Content-Type': 'application/json' , 'Authorization' :'Basic ENCODESTRINGHERE'}   
        self.logger.debug("Fetching basicauth data from " + url)
        try:
            res = requests.get(url, headers=headers)
            return res.json()

        except Exception as e:
            self.logger.erro("get_data failure" + str(e))
            return None

    def print_pretty(self, jsonbytes):
        self.logger.debug("JSON Print Pretty")
        jsonstr = jsonbytes.decode("utf-8")
        on_object = json.loads(jsonstr)
        json_formatted_str = json.dumps(json_object, indent=2)
        print(json_formatted_str)
    
    def store_data(self, item, df):
        del df['measurementType']
        del df['type']
        df = df.apply(pd.to_numeric)
        df['Date'] = pd.to_datetime(df['readingTime'], unit='s')
        df = df.set_index('Date')
        try:
            if item not in self.collection.items:
                self.collection.write(item, df)
            else:
                self.collection.append(item, df)
        except Exception as e:
            print(e)

       
    def get_global_info(self):
        pp = pprint.PrettyPrinter(indent=4)
        gdict = daily.get_http_plain("production.json")
        
        if gdict is None:
            print("no data")
            return
        rdict = {}
        # map the fetched data to items
        rdict[self.items[0]] = gdict['consumption'][0]
        rdict[self.items[1]] = gdict['consumption'][1]
        rdict[self.items[2]] = gdict['production'][1]
        self.rdict = rdict
        for e in rdict:
            df = pd.DataFrame.from_dict(rdict[e], orient='index').T
            self.store_data(e, df) 

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
    daily = Ingest(logger, config)
    while True:
        #Get the data every 10 seconds and store it into the pystore
        daily.get_global_info()
        time.sleep(10)
