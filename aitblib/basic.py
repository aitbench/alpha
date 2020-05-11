import os.path
import yaml
import datetime
# import sys


class Basic():
    def __init__(self, appRoot, db):
        self.db = db
        self.appRoot = appRoot
        # Runner Paths
        self.tmpPath = appRoot + os.path.sep + 'tmp' + os.path.sep
        self.runPath = self.tmpPath + os.path.sep + 'run' + os.path.sep
        self.logPath = appRoot + os.path.sep + 'logs' + os.path.sep
        # Configuration Paths
        self.confPath = appRoot + os.path.sep + 'conf' + os.path.sep
        self.dataConfPath = appRoot + os.path.sep + 'conf' + os.path.sep + 'data' + os.path.sep
        self.conConfPath = appRoot + os.path.sep + 'conf' + os.path.sep + 'conn' + os.path.sep
        # Data paths
        self.dataPath = appRoot + os.path.sep + 'data' + os.path.sep
        self.sampleDataPath = appRoot + os.path.sep + 'data' + os.path.sep + 'samples' + os.path.sep
        self.nuggetDataPath = appRoot + os.path.sep + 'data' + os.path.sep + 'nuggets' + os.path.sep
        # Time format
        self.timeform = '%d/%m/%Y'
        # Bokeh theme
        self.bokehTheme = 'caliber'

    def Hello(self):
        print('Hello this is basic')

    # List of Config files
    def listCfgFiles(self, oftype):
        return [f for f in os.listdir(self.confPath + oftype) if os.path.isfile(os.path.join(self.confPath + oftype, f)) and f != '.keep']

    # List of Data Files
    def listDataFiles(self, oftype):
        return [f for f in os.listdir(self.dataPath + oftype) if os.path.isfile(os.path.join(self.dataPath + oftype, f)) and f != '.keep']

    # Write Config File
    def writeCfgFile(self, oftype, nom, input):
        fname = self.confPath + oftype + os.path.sep + nom + '.yml'
        with open(fname, 'w') as file:
            file.write(input)

    # Read Config File
    def readCfgFile(self, oftype, nom):
        fname = self.confPath + oftype + os.path.sep + nom
        with open(fname, 'r') as file:
            output = yaml.full_load(file)
        return output

    # Get info on all nuggets
    def nuggetsInfo(self, filelist):
        tmpnuggets = []
        tmpinfo = {}
        # Iterate through each file
        for dfile in filelist:
            # Remove extension from filename
            # print(dfile,file=sys.stderr)
            dstr = os.path.splitext(dfile)[0]
            # Split filename into strings
            parts = dstr.split('_')
            # Create temp info from filename
            tmpinfo = {'id': dstr, 'con': parts[0], 'symb': parts[1] + '/' + parts[2], 'timeframe': parts[3],
                       'from': int(parts[4]), 'to': int(parts[5]), 'indi': parts[6], 'depen': parts[7]}
            # Convert ms date to human readable format
            tmpinfo['from'] = datetime.datetime.utcfromtimestamp(tmpinfo['from'] / 1000).strftime(self.timeform)
            tmpinfo['to'] = datetime.datetime.utcfromtimestamp(tmpinfo['to'] / 1000).strftime(self.timeform)
            # Add temp info to array of nuggets
            tmpnuggets.append(tmpinfo)
        return tmpnuggets

    # Get info on single nugget
    def nugInfo(self, nfile):
        ntmpinfo = {}
        # Remove extension from filename
        nfile = os.path.splitext(nfile)[0]
        # Split filename into strings
        parts = nfile.split('_')
        # Create temp info from filename
        ntmpinfo = {'id': nfile, 'con': parts[0], 'symb': parts[1] + '/' + parts[2], 'timeframe': parts[3],
                    'from': int(parts[4]), 'to': int(parts[5]), 'indi': parts[6], 'depen': parts[7]}
        # Convert ms date to human readable format
        ntmpinfo['from'] = datetime.datetime.utcfromtimestamp(ntmpinfo['from'] / 1000).strftime(self.timeform)
        ntmpinfo['to'] = datetime.datetime.utcfromtimestamp(ntmpinfo['to'] / 1000).strftime(self.timeform)
        # Add temp info to array of nuggets
        return ntmpinfo

    # Get info on samples
    def samplesInfo(self, filelist):
        # Init temp variables
        tmpsamples = []
        tmpinfo = {}
        # Iterate through each file
        for sfile in filelist:
            # Remove extension from filename
            sstr = os.path.splitext(sfile)[0]
            # Split filename into strings
            parts = sstr.split('_')
            # Create temp info from filename
            tmpinfo = {'id': sstr, 'con': parts[0], 'symb': parts[1] + '/' + parts[2], 'timeframe': parts[3], 'from': int(parts[4]), 'to': int(parts[5])}
            # Convert ms date to human readable format
            tmpinfo['from'] = datetime.datetime.utcfromtimestamp(tmpinfo['from'] / 1000).strftime(self.timeform)
            tmpinfo['to'] = datetime.datetime.utcfromtimestamp(tmpinfo['to'] / 1000).strftime(self.timeform)
            # Add temp info to array of samples
            tmpsamples.append(tmpinfo)
        return tmpsamples

    # Timeframe to Milliseconds
    def tfToMS(self, tf):
        if 'T' in tf:
            temptf = int(tf.replace('T', ''))
            output = temptf * 60 * 1000
        if 'H' in tf:
            temptf = int(tf.replace('H', ''))
            output = temptf * 60 * 60 * 1000
        return output

    # ClearRunLocks
    def clearRunLocks(self):
        runFiles = [f for f in os.listdir(self.runPath) if os.path.isfile(os.path.join(self.runPath, f)) and f != '.keep']
        for file in runFiles:
            os.remove(self.runPath + file)
