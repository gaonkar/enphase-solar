# Copyright StockAnalytics 2019
import os
import json
import pathlib
import time
import datetime as dt
import configparser
from multiprocessing import Pool
import concurrent.futures
import resource
import shutil

def GetConfigFile(configDir, scriptName):
    '''
        Take the name of the file, strip the extension, concatenate ".ini" and
        return the name

        Parameters
            configDir:      path to config dir
            scriptName:     Name of the script file
    '''
    iniName = scriptName.split('.')[0] + ".ini"
    configPath = os.path.join(configDir, iniName)
    if not os.path.isfile(configPath):
        raise Exception("Config File %s does not exist", configPath)
    return configPath

def CreateDirPath(oPath, logger):
    '''
        Create a Dir path

        Parameters:
            oPath: Path to directory

        Returns
            True if it exists
    '''
    try:
        if not os.path.exists(oPath):
            pathlib.Path(oPath).mkdir(parents=True, exist_ok=True)
            logger.debug("Creating directory on %s", oPath)
            return True
        else:
            logger.debug("Directory %s exists", oPath)
            return False

    except Exception as e:
        logger.error("Unhandled exception %s", str(e))

def ForkFunction(funcName, logger, fanout, pathList):
    '''

        Parameters
            funcName:   function called
            logger:     logging handler
            fanout:     number of parallel jobs
            pathList:   List of paths

        Results
            Array of result objects
    '''
    n_workers = fanout
    outarr = list()
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as executor:
        results = {executor.submit(funcName, pList): pList for pList in pathList}
        for future in concurrent.futures.as_completed(results):
            out = results[future]
            try:
                data = future.result()
                outarr.append(data)
            except Exception as exc:
                logger.error('%s generated an exception: %s' % (out, exc))
            else:
                logger.debug('%s Processed ', out)
    return outarr

def GetMaxMemoryConsumedInMB():
    maxMem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
    return str(round(maxMem,2))


def FlattenDict(pDict, delim):
    def myitems():
        for k, v in pDict.items():
            if isinstance(v, dict):
                for sk, sv in FlattenDict(v, delim).items():
                    yield k + delim + sk, sv
            else:
                yield k, v
    return dict(myitems())


def GetConfigFromDirAndBaseName(cfgPath, baseName):
    '''
        Get the config information and return to caller
    '''
    config = configparser.ConfigParser()
    lConfigPath = GetConfigFile(cfgPath, baseName)
    if os.path.exists(lConfigPath):
        config.read(lConfigPath)
    else:
        raise Exception('missing file %s', lConfigPath)
    return config



def GetConfigFromFilePath(cfgPath):
    '''
        Get the config information and return to caller
    '''
    config = configparser.ConfigParser()
    if os.path.exists(cfgPath):
        config.read(cfgPath)
    else:
        raise Exception('missing file %s', cfgPath)
    for each_section in config.sections():
        for (each_key, each_val) in config.items(each_section):
                print (each_key, each_val)
    return config




def RecursiveDeleteFolder(logger, lpath, realmode = True):
    '''
        Recursive Delete a folder. If test mode is set, we just log the process
    '''

    if realmode:

        logger.debug("shutil rmtree " + lpath)
        if os.path.exists(lpath):
            shutil.rmtree(lpath)
    else:
        print("rm -rf " + lpath)



def StoreJson(logger, pDict, jPath):
    '''
        Wrapper function to store the dictionary into json
    '''
    try:
        logger.debug("Store JSON into '%s' file", jPath)
        F = open(jPath, 'w', encoding='utf-8')
        js = json.dump(pDict, F, ensure_ascii=False,
                       sort_keys = True, indent = 4)
        F.close()
    except Exception as exc:
        logger.error("Saving JSON failed  %s", str(exc))
        F.close()


def LoadJson(logger, jf):
    '''
        Wrapper function to load the json file
    '''
    try:
        logger.debug("Parsing JSON '%s' file", jf)
        if not os.path.exists(jf):
            logger.debug("Failed Parsing JSON '%s' file", jf)
            return None
        F = open(jf)
        js = json.load(F)
        F.close()
        return js
    except Exception as exc:
        logger.error("Invalid format %s in file %s", str(exc), jf)
        F.close()
        return None

def ToDate(datestr):
     return dt.datetime.strptime(datestr, "%Y-%m-%d")
