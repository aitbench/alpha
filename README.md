# AITB

AI Trader Bench Alpha. Currently just downloads the data and nuggets it to visualize it. Build path is now active.

## Requirements
```pip
pip install -r requirements.txt
```
## Additional Requirements
#### TA-Lib - Technical indicators and candlestick patterns
Great installation instructions in https://mrjbq7.github.io/ta-lib/install.html so I won't reinvent the wheel.
#### Snappy - Google compression that's pointless other than getting data off Kaggle
On **Windows**: (tested)

Easiest way of doing this was going to https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-snappy

Download python_snappy‑0.5.4‑**cp37**‑cp37m‑win_amd64.whl matches to Python 3.7 on a 64 bit system
```cmd
pip install python_snappy‑0.5.4‑cp37‑cp37m‑win_amd64.whl
```
On **DEB-based Linux**: (untested)
```bash
sudo apt-get install libsnappy-dev
pip install python-snappy 
```
On **RPM-based Linux**: (untested)
```sh
sudo yum install libsnappy-devel
pip install python-snappy 
```
On **Mac**: (tested with Mike)
```brew
brew install snappy
pip install python-snappy
```

## Run
```bash
python app.py
```
Then go to http://localhost:5000/register

Then sign in http://localhost:5000/login

If you wish to use an SQL server instead of SQLite go to http://localhost:5000/setup and restart the app.

## Free Data
##### Crypto Data
https://www.kaggle.com/jorijnsmit/binance-full-history

Binance is a decent exchange with a proven track record. All data going back to starting pairs. Thanks Pierre! *Requires Signup*

##### Forex Data
https://www.dukascopy.com/swiss/english/marketwatch/historical/

Dukascopy has always been an excellent source of data for backtesting. 1M bars go back for 3 years which is enough. Thanks Huub! *Requires Signup*

##### Stock Data

No idea yet of a good source which has 1M bars with volume. Probably IB is a good source:
https://interactivebrokers.github.io/tws-api/historical_data.html

## Diagrams
```mermaid
graph LR
    A>Connection] --> B[(Data 1m)]-->C[Samples]
    D([TimeFrame])-->C
    C-->E[Nuggets]
    F([Riches])-->G(Enrichments X)-->E
    H([Dependant y])-->E
    E-->I((Observatorium))
    E-->J((AI))
    I-->K[View]
    I-->L[Correlate]
    I-->M[Feature Selection]
```
