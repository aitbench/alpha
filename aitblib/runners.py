import os
from datetime import datetime
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
            file.write(str(datetime.now()) + " -- Testing timing and threads\n")
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
        # file.write(str(datetime.now())+" --Testing\n")
        # Test if already running
        if os.path.exists(dname):
            return
        # Write lock file
        with open(dname, 'w') as file:
            file.write(str(datetime.now()))
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
                            data = tmpex.fetch_ohlcv(tmpDataConf['symb'], '1m', tmpDataConf['start'])
                    else:
                        if tmpex.has['fetchOHLCV']:
                            # Check for recent additions
                            result = self.db.session.execute('SELECT * from ' + tmpDataConf['id']).fetchall()
                            # Drop results to dataFrame
                            datadf = pd.DataFrame(result, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
                            ldate = datetime.utcfromtimestamp(datadf['Date'].iloc[-1] / 1000).strftime('%Y-%m-%d %H:%M')
                            with open(dlog, 'a') as file:
                                file.write(str(datetime.now()) + " -- Downloading " + tmpDataConf['symb'] + " starting from " + ldate + "\n")
                            data = tmpex.fetch_ohlcv(tmpDataConf['symb'], '1m', int(datadf['Date'].iloc[-1]))
                    # Write results to database
                    for datarow in data:
                        self.db.session.execute(sqlpre + tmpDataConf['id'] + ' VALUES (' + str(datarow[0]) + ',' + str(datarow[1]) + ',' + str(datarow[2]) + ',' + str(datarow[3]) + ',' + str(datarow[4]) + ',' + str(datarow[5]) + ')')
                    # Commit database entries
                    self.db.session.commit()
                except (ccxt.ExchangeError, ccxt.NetworkError) as error:
                    # Catch most common errors
                    with open(dlog, 'a') as file:
                        file.write(str(datetime.now()) + " --" + type(error).__name__ + "--" + error.args + "\n")
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
                saveConf = yaml.dump(tmpDataConf, default_flow_style=False, sort_keys=False)
                # Cfg File
                self.writeCfgFile('data', id, saveConf)
        # Remove File Lock
        os.remove(dname)

    def backTest(self):
        # Create file and path
        bname = self.runPath + 'bt.run'
        blog = self.logPath + 'bt.log'
        # Test if already running
        if os.path.exists(bname):
            return
        # Write lock file
        with open(bname, 'w') as file:
            file.write(str(datetime.now()))
        # Get list of data files
        btCfgs = self.listCfgFiles('bt')
        for bfile in btCfgs:
            btConf = self.readCfgFile('bt', bfile)
            if btConf['run']:
                # Log starting point of backtest
                with open(blog, 'a') as file:
                    file.write(str(datetime.now()) + " -- Backtest of " + btConf['name'] + " started...\n")
                # Run backtest
                with open(self.btDataPath + btConf['id'] + '.py') as infile:
                    exec(infile.read())
                # Log enpoint of backtest
                with open(blog, 'a') as file:
                    file.write(str(datetime.now()) + " -- Backtest of " + btConf['name'] + " finished!\n")
                # Move reports
                os.replace('Report.html', self.stBtPath + btConf['id'] + '_report.html')
                # Move Charts
                os.replace(btConf['name'] + '.html', self.stBtPath + btConf['id'] + '_chart.html')
                # Read results
                results = pd.read_csv(self.btDataPath + btConf['id'] + '_results.csv')
                # Turn off Running
                btConf['run'] = False
                btConf['lastrun'] = str(datetime.now())
                fPerc = round(float(results['0'][6]), 2)
                btConf['fperc'] = str(fPerc)
                hPerc = round(((float(results['0'][5]) - float(btConf['cash'])) / float(btConf['cash'])) * 100, 2)
                btConf['hperc'] = str(hPerc)
                DD = round(float(results['0'][8]), 2)
                btConf['dd'] = str(DD)
                # Convert Dict to YAML
                saveConf = yaml.dump(btConf, default_flow_style=False, sort_keys=False)
                # Save new config file
                self.writeCfgFile('bt', btConf['id'], saveConf)
        # Remove File Lock
        os.remove(bname)
