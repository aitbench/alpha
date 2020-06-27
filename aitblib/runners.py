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
                            result = self.db.session.execute('SELECT * from ' + tmpDataConf['id'] + ' ORDER BY Date DESC LIMIT 1').fetchall()
                            self.db.session.commit()
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
                self.ll(tmpDataConf)
                # Convert Dict to YAML
                saveConf = yaml.dump(tmpDataConf, default_flow_style=False, sort_keys=False)
                # Cfg File
                self.writeCfgFile('data', id, saveConf)
        # Remove File Lock
        os.remove(dname)
        # Close DB Connection

    def dataUpload(self):
        # Create file and path
        uname = self.runPath + 'dataUpload.run'
        ulog = self.logPath + 'dataUpload.log'
        # Test if already running
        if os.path.exists(uname):
            return
        # Write lock file
        with open(uname, 'w') as file:
            file.write(str(datetime.now()))
        # Get list of data files
        upFiles = self.listUpFiles()
        for fname in upFiles:
            # Split file into extension and filename
            nom, ext = os.path.splitext(fname)
            ffname = os.path.join(self.upPath, fname)
            updf = pd.DataFrame()
            if ext == '.csv':
                updf = pd.read_csv(ffname)
            if ext == '.feather':
                updf = pd.read_feather(ffname)
            if ext == '.parquet':
                updf = pd.read_parquet(ffname, engine='fastparquet')
            if ext == '.pickle':
                updf = pd.read_pickle(ffname)
            # Test for created index
            if updf.index[0] == 0:
                for col in updf.columns:
                    # Test column automatically for date
                    if type(updf[col][0]) is pd.Timestamp:
                        # Set column as datetime and make it an index
                        updf[col] = pd.to_datetime(updf[col])
                        updf.set_index(col, inplace=True)
                        break
                    elif self.is_date(updf[col][0]):
                        # Set column as datetime and make it an index
                        updf[col] = pd.to_datetime(updf[col])
                        updf.set_index(col, inplace=True)
                        break
            with open(ulog, 'w') as file:
                file.write(str(datetime.now()) + ' -- Starting upload of ' + str(nom) + "...\n")
            # print(updf.index.astype(int)/1000000,file=sys.stderr)
            if 'sqlite' in str(self.db.engine.url):
                sqlpre = 'INSERT OR IGNORE INTO '
            else:
                sqlpre = 'INSERT IGNORE INTO '
            rcount = 0
            everyXrows = 5000
            if 'open' in updf.columns:
                for index, dr in updf.iterrows():
                    rcount += 1
                    sqlins = sqlpre + nom + ' VALUES (' + str(int(index.value / 1000000)) + ',' + str(dr['open']) + ',' + str(dr['high']) + ',' + str(dr['low']) + ',' + str(dr['close']) + ',' + str(dr['volume']) + ')'
                    # print(sqlins,file=sys.stderr)
                    self.db.session.execute(sqlins)
                    if rcount % everyXrows == 0:
                        with open(ulog, 'a+') as file:
                            file.write(str(datetime.now()) + ' -- Inserting to ' + str(nom) + ' up to ' + str(index) + "\n")
                        self.db.session.commit()
                self.db.session.commit()
            if 'Open' in updf.columns:
                for index, dr in updf.iterrows():
                    rcount += 1
                    sqlins = sqlpre + nom + ' VALUES (' + str(int(index.value / 1000000)) + ',' + str(dr['Open']) + ',' + str(dr['High']) + ',' + str(dr['Low']) + ',' + str(dr['Close']) + ',' + str(dr['Volume']) + ')'
                    # print(sqlins,file=sys.stderr)
                    self.db.session.execute(sqlins)
                    if rcount % everyXrows == 0:
                        with open(ulog, 'a+') as file:
                            file.write(str(datetime.now()) + ' -- Inserting to ' + str(nom) + ' up to ' + str(index) + "\n")
                        self.db.session.commit()
                self.db.session.commit()
            os.remove(ffname)
        os.remove(uname)

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
                # Move Charts
                os.replace(btConf['id'] + '.html', self.stBtPath + btConf['id'] + '_chart.html')
        # Remove File Lock
        os.remove(bname)
