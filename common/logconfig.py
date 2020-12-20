#Copyright 2019 Stock Analytics
import logging
import logging.config
import configparser
import argparse
import json
import os
import unittest
import sys
import utils

class LogConfig:

    def __init__(self, configDir, config, basename):
        try:
            logFileName = basename + ".log"
            if config.has_option('LOGGING', 'filePath'):
                self.logPath = os.path.join(config['LOGGING']['filepath'], logFileName)
            else:
                self.logPath = os.path.join("/tmp", logFileName)
            lDictPath = os.path.join(configDir, "logging.json")

            #set the log type
            if config.has_option('LOGGING', 'logType'):
                self.logType = config['LOGGING']['logType']
            else:
                self.logType = "console"
            #Load the default json file
            F = open(lDictPath, 'r')
            self.logDict = json.loads(F.read())
            F.close()
            self.logDict["disable_existing_loggers"] = False
            self.logDict["handlers"]["file"]["filename"] = self.logPath

        except Exception as e:
            raise Exception("Unhandled exception")

    def ConfigLogToScreenOnly(self):
        logging.config.dictConfig(self.logDict)
        return logging.getLogger("console")

    def ConfigLogToFileOnly(self):
        logging.config.dictConfig(self.logDict)
        print("Logging to file %", self.logPath)
        return logging.getLogger("file")

    def ConfigLog(self, logType):
        logging.config.dictConfig(self.logDict)
        if logType == "both":
            print("Logging to file %", self.logPath)
            return logging.getLogger("both")
        if logType == "file":
            return self.ConfigLogToFileOnly()
        return logging.getLogger("console")

class TestSSLogger(unittest.TestCase):
    configDir = None

    def test_onscreenonly(self):

        baseName = os.path.basename(__file__)
        config = configparser.ConfigParser()
        lConfigPath = utils.GetConfigFile(self.configDir, baseName)
        config.read(lConfigPath)
        ss = LogConfig(self.configDir, config, baseName)
        log = ss.ConfigLogToScreenOnly()
        log.debug("test")

    def test_onfileonly(self):
        baseName = os.path.basename(__file__)
        config = configparser.ConfigParser()
        lConfigPath = utils.GetConfigFile(self.configDir, baseName)
        config.read(lConfigPath)
        ss = LogConfig(self.configDir, config, baseName)
        if os.path.isfile(ss.logPath):
            os.remove(ss.logPath)
        log = ss.ConfigLogToFileOnly()
        log.debug("file")

# main() will be executed
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--configDir', help='path to config directory',
                        required=True)
    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()

    # Set the class object for logging information
    TestSSLogger.configDir = args.configDir
    # Set the sys.argv to the unittest_args (leaving sys.argv[0] alone)
    sys.argv[1:] = args.unittest_args
    unittest.main()
