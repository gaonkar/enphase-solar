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
from suntime import Sun, SunTimeException
import datetime 

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
        self.password='000102'
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
        '''
            Using requests from python does seem to honor basic auth. It could be becaus envoy is an http url
        '''
        import subprocess

        url = os.path.join(self.url, urlpath)

        try:
            cmd = "curl -s --anyauth --user %s:%s %s" % (self.username, self.password, url)
            cmd = cmd.split(" ")
            print(cmd)
            result = subprocess.run(cmd, stdout=subprocess.PIPE)
            result = result.stdout.decode('ascii')
            result = result.replace('\n','')
            #result = result.replace('"','\\"')
            return json.loads(result)
        
        except Exception as e:
            self.logger.error("get_data failure" + str(e))
            return None

    
    def store_data(self, item, df):
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
            del df['measurementType']
            del df['type']
            df = df.apply(pd.to_numeric)
            df['Date'] = pd.to_datetime(df['readingTime'], unit='s')
            df = df.set_index('Date')
            self.store_data(e, df) 
    
    def get_inverters_info(self):
        gdict = daily.get_http_basicauth("api/v1/production/inverters")
        
        if gdict is None:
            print("no data")
            return
        epoch_time = int(time.time())
        df = pd.DataFrame(gdict)
        df.insert(0, 'Date', range(epoch_time, epoch_time + len(df)))
        df = df.apply(pd.to_numeric)
        df['Date'] = pd.to_datetime(df['Date'], unit='s')
        df = df.set_index('Date')
        #print(df)
        self.store_data("invertors", df)

class Localize:
    '''
        Class to determine local timezone and manage local API
    '''
    def __init__(self, logger, config):

        self.logger = logger
        self.latitude = float(config['DEFAULT']['latitude'])
        self.longitude = float(config['DEFAULT']['longitude'])
        
        sun = Sun(self.latitude, self.longitude)
        today_sr = sun.get_local_sunrise_time() 
        today_ss = sun.get_local_sunset_time() 

        self.sunrise = today_sr.strftime('%H:%M')
        self.sunset = today_ss.strftime('%H:%M')
        logger.debug("Sunrise:" + self.sunrise + "Sunset:" + self.sunset)
    
    def isSunVisible(self):
        t0 = time.time()
        timestr = time.strftime("%H:%M",time.localtime(t0)) 
        logger.debug("Sunrise:" + self.sunrise + "Sunset:" + self.sunset + "CurTime:" + timestr)
        if timestr >= self.sunrise and timestr <= self.sunset:
            return True
        return False

    def isSunSet(self):
        t0 = time.time()
        timestr = time.strftime("%H:%M",time.localtime(t0)) 
        logger.debug("Sunrise:" + self.sunrise + "Sunset:" + self.sunset + "CurTime:" + timestr)
        if timestr > self.sunset:
            return True
        return False
    



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
    bconfig = utils.GetConfigFromDirAndBaseName(args.configDir, baseName)
    private = utils.GetConfigFromFilePath(bconfig['DEFAULT']['private'])

    #Get the logger setup
    logConfig = LogConfig(args.configDir, bconfig, baseName)
    logger = logConfig.ConfigLog(bconfig['LOGGING']['logType'])
   
    local = Localize(logger, private)
    daily = Ingest(logger, bconfig)
    
    while True:
        while local.isSunVisible():
            daily.get_global_info()
            daily.get_inverters_info()
            time.sleep(20)
        time.sleep(60)
        print("waiting")
