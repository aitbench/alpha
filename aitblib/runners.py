import os
import datetime
import sys
import yaml
import ccxt
# AITB Basic base class
from .basic import Basic
from pandas import DataFrame


class Runner(Basic):

    def test(self):
        # Create lock file
        tname = self.logPath + 'test.log'
        with open(tname, 'a') as file:
            file.write(str(datetime.datetime.now()) + " -- Testing timing and threads\n")
        # print('TesterRunner',file=sys.stderr)

    def dataDownload(self, aggro):
        # Create file and path
        if(aggro):
            dpre = 'dataDownloadAggro'
        else:
            dpre = 'dataDownload'
        dname = self.runPath + dpre + '.run'
        # Test if already running
        if os.path.exists(dname):
            with open(self.logPath + dpre + '.log', 'a') as file:
                file.write(str(datetime.datetime.now()) + " -- Data Downloader lockfile found!!\n")
            return
        # Write lock file
        with open(dname, 'w') as file:
            file.write(str(datetime.datetime.now()))
        # Get list of data files
        dataCfgs = self.listCfgFiles('data')
        for file in dataCfgs:
            tmpDataConf = self.readCfgFile('data', file)
            if tmpDataConf['enabled'] and tmpDataConf['aggro'] == aggro:
                # Create exchange instance
                ex_class = getattr(ccxt, tmpDataConf['con'])
                tmpex = ex_class({'timeout': 10000, 'enableRateLimit': True})
                data = ""
                try:
                    # Check if data empty else start from last entry
                    if tmpDataConf['count'] == 0:
                        if tmpex.has['fetchOHLCV']:
                            # print('No Data start Fresh',file=sys.stderr)
                            data = tmpex.fetch_ohlcv(tmpDataConf['symb'], '1m', tmpDataConf['start'])
                    else:
                        if tmpex.has['fetchOHLCV']:
                            # Check for recent additions
                            result = self.db.session.execute('SELECT * from ' + tmpDataConf['id']).fetchall()
                            # Drop results to dataFrame
                            datadf = DataFrame(result, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                            # print('Data Found start from: #'+str(datadf['date'].iloc[-1])+'#',file=sys.stderr)
                            data = tmpex.fetch_ohlcv(tmpDataConf['symb'], '1m', int(datadf['date'].iloc[-1]))
                    # Write results to database
                    for datarow in data:
                        self.db.session.execute('INSERT OR IGNORE INTO ' + tmpDataConf['id'] + ' VALUES (' + str(datarow[0]) + ',' + str(datarow[1]) + ',' + str(datarow[2]) + ',' + str(datarow[3]) + ',' + str(datarow[4]) + ',' + str(datarow[5]) + ')')
                    # Commit database entries
                    self.db.session.commit()
                except BaseException:
                    print('Pull data Error', file=sys.stderr)
                # Check for recent additions
                result = self.db.session.execute('SELECT * from ' + tmpDataConf['id']).fetchall()
                # Drop results to dataFrame
                datadf = DataFrame(result, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                # Create and save head tail and count
                tmpDataConf['head'] = datadf.values.tolist()[0]
                tmpDataConf['tail'] = datadf.values.tolist()[-1]
                tmpDataConf['end'] = datadf.values.tolist()[-1][0]
                tmpDataConf['count'] = str(datadf.shape[0])
                id = tmpDataConf['id']
                # Convert Dict to YAML
                saveConf = yaml.dump(tmpDataConf)
                # Cfg File
                self.writeCfgFile('data', id, saveConf)
        # Remove File Lock
        os.remove(dname)
