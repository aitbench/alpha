import os
import datetime
import sys
import yaml
import ccxt
import pandas as pd
# AITB Basic base class
from .basic import Basic


class Runner(Basic):

    def test(self):
        # Create lock file
        tname = self.logPath + 'test.log'
        with open(tname, 'a') as file:
            file.write(str(datetime.datetime.now()) + " -- Testing timing and threads\n")
        print('TesterRunner', file=sys.stderr)

    def dataDownload(self, aggro):
        # Create file and path
        if(aggro):
            dpre = 'dataDownloadAggro'
        else:
            dpre = 'dataDownload'
        dname = self.runPath + dpre + '.run'
        dlog = self.logPath + dpre + '.log'
        # Testing logging
        # with open(dlog, 'a') as file:
        # file.write(str(datetime.datetime.now())+" --Testing\n")
        # Test if already running
        if os.path.exists(dname):
            return
        # Write lock file
        with open(dname, 'w') as file:
            file.write(str(datetime.datetime.now()))
        # Create SQL pre insert
        if 'sqlite' in str(self.db.engine.url):
            sqlpre = 'INSERT OR IGNORE INTO '
        else:
            sqlpre = 'INSERT IGNORE INTO '
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
                            datadf = pd.DataFrame(result, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
                            # print('Data Found start from: #'+str(datadf['date'].iloc[-1])+'#',file=sys.stderr)
                            data = tmpex.fetch_ohlcv(tmpDataConf['symb'], '1m', int(datadf['Date'].iloc[-1]))
                    # Write results to database
                    for datarow in data:

                        self.db.session.execute(sqlpre + tmpDataConf['id'] + ' VALUES (' + str(datarow[0]) + ',' + str(datarow[1]) + ',' + str(datarow[2]) + ',' + str(datarow[3]) + ',' + str(datarow[4]) + ',' + str(datarow[5]) + ')')
                    # Commit database entries
                    self.db.session.commit()
                except (ccxt.ExchangeError, ccxt.NetworkError) as error:
                    # Catch most common errors
                    with open(dlog, 'a') as file:
                        file.write(str(datetime.datetime.now()) + " --" + type(error).__name__ + "--" + error.args + "\n")
                    break
                # Check for recent additions
                result = self.db.session.execute('SELECT * from ' + tmpDataConf['id']).fetchall()
                # Drop results to dataFrame
                datadf = pd.DataFrame(result, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
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
