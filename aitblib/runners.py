import os
from datetime import datetime
import time
import sys
import ccxt
import pandas as pd
import pickle as pkl
# AITB Basic base class
from .basic import Basic
# Trends
from pytrends.request import TrendReq
# Feed reader
import feedparser
# Textblob
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
# Vader
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


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
                # Cfg File
                self.writeCfgFile('data', id, tmpDataConf)
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
                # Update info
                btConf['lastrun'] = str(datetime.now())
                fPerc = round(float(results['0'][6]), 2)
                btConf['fperc'] = str(fPerc)
                hPerc = round(((float(results['0'][5]) - float(btConf['cash'])) / float(btConf['cash'])) * 100, 2)
                btConf['hperc'] = str(hPerc)
                DD = round(float(results['0'][8]), 2)
                btConf['dd'] = str(DD)
                # Save new config file
                self.writeCfgFile('bt', btConf['id'], btConf)
                # Move Charts
                os.replace(btConf['id'] + '.html', self.stBtPath + btConf['id'] + '_chart.html')
        # Remove File Lock
        os.remove(bname)

    def googleTrends(self):
        # Create file and path
        gname = self.runPath + 'googleTrends.run'
        glog = self.logPath + 'googleTrends.log'
        # Test if already running
        if os.path.exists(gname):
            return
        # Write lock file
        with open(gname, 'w') as file:
            file.write(str(datetime.now()))
        # Get list of data files
        gCfgs = self.listCfgFiles('senttrend')
        for gfile in gCfgs:
            gConf = self.readCfgFile('senttrend', gfile)
            if gConf['enabled']:
                # Log starting point of backtest
                with open(glog, 'a') as file:
                    file.write(str(datetime.now()) + " -- Trending of " + gConf['keyword'] + " started...\n")
                    # Create ID
                # Create ID
                # id = gConf['keyword'].replace(' ','_').lower()+ '_' + gConf['period'] + '_' + gConf['cat']
                # Create period name
                if gConf['period'] == '4h':
                    per = 'now 4-H'
                if gConf['period'] == '1D':
                    per = 'now 1-d'
                if gConf['period'] == '1W':
                    per = 'now 7-d'
                # Initialize pyTrend
                pytrend = TrendReq(hl='en-US', tz=0, timeout=(10, 25))
                # Get trends
                pytrend.build_payload([gConf['keyword']], cat=gConf['cat'], timeframe=per, geo=gConf['geo'], gprop=gConf['type'])
                # Create Dataframe
                tdf = pytrend.interest_over_time()
                # Insert into database
                tinms = int(round(time.time() * 1000))
                lastval = tdf[gConf['keyword']].tail(1)[0]
                sqlinstrend = 'INSERT into trend_' + gConf['id'] + ' VALUES (' + str(tinms) + ',' + str(lastval) + ')'
                try:
                    self.db.session.execute(sqlinstrend)
                except BaseException:
                    # Create Database table class
                    table_creation_sql = 'CREATE TABLE IF NOT EXISTS trend_' + gConf['id'] + ' (Date BIGINT NOT NULL, PercVal INT, PRIMARY KEY(Date))'
                    # Create SQL table
                    self.db.session.execute(table_creation_sql)
                    self.db.session.commit()
                    self.db.session.execute(sqlinstrend)
                self.db.session.commit()
                # Echo df
                # self.ll(tdf.tail(1))
                # self.ll(tdf[gConf['keyword']].tail(1)[0])
        # Remove File Lock
        os.remove(gname)

    def sentiRSS(self):
        # Create file and path
        rname = self.runPath + 'sentiRSS.run'
        # rlog = self.logPath+'sentiRSS.log'
        # Test if already running
        if os.path.exists(rname):
            return
        # Write lock file
        with open(rname, 'w') as file:
            file.write(str(datetime.now()))
        # Get list of data files and nlp setup
        rCfgs = self.listCfgFiles('sentrss')
        nlp = self.readCfgFile('sentnlp', 'sent-ai.yml')
        # Itterate through files
        for rfile in rCfgs:
            rConf = self.readCfgFile('sentrss', rfile)
            # Check if enabled and ready to parse
            if rConf['enabled']:
                # Parse RSS via FeedParser
                raw = feedparser.parse(rConf['url'])
                pos = neg = neu = comp = 0
                postcount = 0
                for post in raw.entries:
                    postcount = + 1
                    # Select data from parse
                    if rConf['using'] == 'summary':
                        rssdata = post.summary
                    if rConf['using'] == 'title':
                        rssdata = post.title
                    # Check which AI to use for sentiment
                    if nlp['ai'] == 'text':
                        # Train and save Analyser
                        nbFile = self.dataPath + "textBlobNB.pkl"
                        if os.path.exists(nbFile):
                            load_nb = open(nbFile, "rb")
                            nbAnalyse = pkl.load(load_nb)
                            load_nb.close()
                        else:
                            nbAnalyse = NaiveBayesAnalyzer()
                            nbAnalyse.train()
                            save_nb = open(nbFile, "wb")
                            pkl.dump(nbAnalyse, save_nb)
                            save_nb.close()
                        tb = TextBlob(rssdata, analyzer=nbAnalyse)
                        pos = pos + tb.sentiment[1]
                        neg = neg + tb.sentiment[2]
                    if nlp['ai'] == 'vader':
                        vader = SentimentIntensityAnalyzer()
                        v = vader.polarity_scores(rssdata)
                        pos = pos + v['pos']
                        neg = neg + v['neg']
                        neu = neu + v['neu']
                        comp = comp + v['compound']
                    if nlp['ai'] == 'distilbert':
                        # Huggingface
                        from transformers import pipeline
                        # Create Huggingface transformers pipeline
                        huggy = pipeline('sentiment-analysis')
                        hugresp = huggy(rssdata)
                        # Workout if positive or negative
                        label = hugresp[0]['label'][0:3]
                        if label == "NEG":
                            hugneg = hugresp[0]['score']
                            hugpos = 0
                        if label == "POS":
                            hugneg = 0
                            hugpos = hugresp[0]['score']
                        pos = pos + hugpos
                        neg = neg + hugneg
                # Workout all totals
                pos = float("{:.2f}".format(pos / postcount))
                neg = float("{:.2f}".format(neg / postcount))
                neu = float("{:.2f}".format(neu / postcount))
                comp = float("{:.2f}".format(comp / postcount))
                if pos > neg:
                    overall = 1
                else:
                    overall = 0
                # Check results
                # self.ll('Pos:'+str(pos))
                # self.ll('Neg:'+str(neg))
                # self.ll('Comp:'+str(comp))
                # Insert to DB
                tinms = int(round(time.time() * 1000))
                sqlinsrss = 'INSERT into rss_' + rConf['id'] + ' VALUES (' + str(tinms) + ',' + str(overall) + ',' + str(pos) + ',' + str(neg) + ',' + str(neu) + ',' + str(comp) + ')'
                try:
                    self.db.session.execute(sqlinsrss)
                except BaseException:
                    # Create Database table class
                    table_creation_sql = 'CREATE TABLE IF NOT EXISTS rss_' + rConf['id'] + ' (Date BIGINT NOT NULL, Overall INT, Pos FLOAT, Neg FLOAT, Neu FLOAT, Comp FLOAT, PRIMARY KEY(Date))'
                    # Create SQL table
                    self.db.session.execute(table_creation_sql)
                    self.db.session.commit()
                    self.db.session.execute(sqlinsrss)
                self.db.session.commit()
        os.remove(rname)
