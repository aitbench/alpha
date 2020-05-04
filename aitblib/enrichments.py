# Import base class
from .basic import Basic
import talib as ta
from scipy.signal import argrelextrema
import numpy as np

class Enrichment():

    def test(self):
        print('########################', file=sys.stderr)
        print('Enrichment Helper Class', file=sys.stderr)
        print('########################', file=sys.stderr)

    def listIndi(self):
        overlaps = {'bbands':'Bollinger Bands',
                    'mama':'MESA Adaptive Moving Average',
                    'dema':'Double Exponential Moving Average',
                    'ht_trendline':'Hilbert Transform - Instantaneous Trendline',
                    'kama':'Kaufman Adaptive Moving Average',
                    'ma':'Moving average',
                    'midpoint':'MidPoint over period',
                    'midprice':'Midpoint Price over period',
                    'sar':'Parabolic SAR',
                    'sarext':'Parabolic SAR - Extended',
                    'sma':'Simple Moving Average',
                    't3':'Triple Exponential Moving Average (T3)',
                    'tema':'Triple Exponential Moving Average',
                    'trima':'Triangular Moving Average',
                    'wma':'Weighted Moving Average'}
        momentum = {'adx':'Average Directional Movement Index',
                    'adxr':'Average Directional Movement Index Rating',
                    'apo':'Absolute Price Oscillator',
                    'aroon':'Aroon',
                    'aroonosc':'Aroon Oscillator',
                    'bop':'Balance Of Power',
                    'cci':'Commodity Channel Index',
                    'cmo':'Chande Momentum Oscillator',
                    'dx':'Directional Movement Index',
                    'macd':'Moving Average Convergence/Divergence',
                    'mfi':'Money Flow Index',
                    'mom':'Momentum',
                    'ppo':'Percentage Price Oscillator',
                    'roc':'Rate of change : ((price/prevPrice)-1)*100',
                    'rocp':'Rate of change Percentage: (price-prevPrice)/prevPrice',
                    'rsi':'Relative Strength Index',
                    'trix':'1-day Rate-Of-Change (ROC) of a Triple Smooth EMA',
                    'ultosc':'Ultimate Oscillator',
                    'willr':'Williams %R'}
        volume = {'ad':'Chaikin A/D Line',
                    'adosc':'Chaikin A/D Oscillator',
                    'obv':'On Balance Volume'}
        volitility = {'atr':'Average True Range',
                        'natr':'Normalized Average True Range',
                        'trange':'True range'}
        price = {'avgprice':'Average Price',
                'medprice':'Median Price',
                'typprice':'Typical Price',
                'wclprice':'Weighted Close Price'}
        pattern = {'cdl2crows':'Two Crows',
                'cdl3blackcrows':'Three Black Crows',
                'cdl3inside':'Three Inside Up/Down',
                'cdl3linestrike':'Three-Line Strike',
                'cdl3outside':'Three Outside Up/Down',
                'cdl3starsinsouth':'Three Stars In The South',
                'cdl3whitesoldiers':'Three Advancing White Soldiers',
                'cdlabandonedbaby':'Abandoned Baby',
                'cdladvanceblock':'Advance Block',
                'cdlbelthold':'Belt-hold',
                'cdlbreakaway':'Breakaway',
                'cdlclosingmarubozu':'Closing Marubozu',
                'cdlconcealbabyswall':'Concealing Baby Swallow',
                'cdlcounterattack':'Counterattack',
                'cdldarkcloudcover':'Dark Cloud Cover',
                'cdldoji':'Doji',
                'cdldojistar':'Doji Star',
                'cdldragonflydoji':'Dragonfly Doji',
                'cdlengulfing':'Engulfing Pattern',
                'cdleveningdojistar':'Evening Doji Star',
                'cdleveningstar':'Evening Star',
                'cdlgapsidesidewhite':'Up/Down-gap side-by-side white lines',
                'cdlgravestonedoji':'Gravestone Doji',
                'cdlhammer':'Hammer',
                'cdlhangingman':'Hanging Man',
                'cdlharami':'Harami Pattern',
                'cdlharamicross':'Harami Cross Pattern',
                'cdlhighwave':'High-Wave Candle',
                'cdlhikkake':'Hikkake Pattern',
                'cdlhikkakemod':'Modified Hikkake Pattern',
                'cdlhomingpigeon':'Homing Pigeon',
                'cdlidentical3crows':'Identical Three Crows',
                'cdlinneck':'In-Neck Pattern',
                'cdlinvertedhammer':'Inverted Hammer',
                'cdlkicking':'Kicking',
                'cdlkickingbylength':'Kicking - bull/bear determined by the longer marubozu',
                'cdlladderbottom':'Ladder Bottom',
                'cdllongleggeddoji':'Long Legged Doji',
                'cdllongline':'Long Line Candle',
                'cdlmarubozu':'Marubozu',
                'cdlmatchinglow':'Matching Low',
                'cdlmathold':'Mat Hold',
                'cdlmorningdojistar':'Morning Doji Star',
                'cdlmorningstar':'Morning Star',
                'cdlonneck':'On-Neck Pattern',
                'cdlpiercing':'Piercing Pattern',
                'cdlrickshawman':'Rickshaw Man',
                'cdlrisefall3methods':'Rising/Falling Three Methods',
                'cdlseparatinglines':'Separating Lines',
                'cdlshootingstar':'Shooting Star',
                'cdlshortline':'Short Line Candle',
                'cdlspinningtop':'Spinning Top',
                'cdlstalledpattern':'Stalled Pattern',
                'cdlsticksandwich':'Stick Sandwich',
                'cdltakuri':'Takuri (Dragonfly Doji with very long lower shadow)',
                'cdltasukigap':'Tasuki Gap',
                'cdlthrusting':'Thrusting Pattern',
                'cdltristar':'Tristar Pattern',
                'cdlunique3river':'Unique 3 River',
                'cdlupsidegap2crows':'Upside Gap Two Crows',
                'cdlxsidegap3methods':'Upside/Downside Gap Three Methods'}
        stats = {'beta':'Beta',
                'correl':'Pearsons Correlation Coefficient',
                'linearreg':'Linear Regression',
                'linearreg_angle':'Linear Regression Angle',
                'linearreg_intercept':'Linear Regression Intercept',
                'linearreg_slope':'Linear Regression Slope',
                'stddev':'Standard Deviation',
                'tsf':'Time Series Forecast',
                'var':'Variance'}
        all = {'Overlap Studies':overlaps,
                'Momentum Indicators':momentum,
                'Volume Indicators':volume,
                'Volitility':volitility,
                'Price':price,
                'Pattern':pattern,
                'Stats':stats}
        return all

    def addIndi(self, enrich, endf):
        # Overlays
        if enrich == 'bbands':
            bbup,bbmid,bblow = ta.BBANDS(endf['close'], timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
            endf.insert(0,column='bblow',value=bblow)
            endf.insert(0,column='bbmid',value=bbmid)
            endf.insert(0,column='bbup',value=bbup)
            return endf
        if enrich == 'mama':
            mama,fama = ta.MAMA(endf['close'])
            endf.insert(0,column='fama',value=fama)
            endf.insert(0,column='mama',value=mama)
            return endf
        if enrich == 'dema':
            endf.insert(0,column='dema',value=ta.DEMA(endf['close'],timeperiod=30))
            return endf
        if enrich == 'ema':
            endf.insert(0,column='ema',value=ta.EMA(endf['close'],timeperiod=30)) # Unstable period
            return endf
        if enrich == 'ht_trendline':
            endf.insert(0,column='ht_trendline',value=ta.HT_TRENDLINE(endf['close'])) # Unstable period
            return endf
        if enrich == 'kama':
            endf.insert(0,column='kama',value=ta.KAMA(endf['close'],timeperiod=30)) # Unstable period
            return endf
        if enrich == 'ma':
            endf.insert(0,column='ma',value=ta.MA(endf['close'],timeperiod=30,matype=0))
            return endf
        if enrich == 'midpoint':
            endf.insert(0,column='midpoint',value=ta.MIDPOINT(endf['close'],timeperiod=14))
            return endf
        if enrich == 'midprice':
            endf.insert(0,column='midprice',value=ta.MIDPRICE(endf['high'],endf['low'],timeperiod=14))
            return endf
        if enrich == 'sar':
            endf.insert(0,column='sar',value=ta.SAR(endf['high'],endf['low'],acceleration=0, maximum=0))
            return endf
        if enrich == 'sarext':
            endf.insert(0,column='sarext',value=ta.SAREXT(endf['high'],endf['low'],startvalue=0,offsetonreverse=0,accelerationinitlong=0,accelerationlong=0,accelerationmaxlong=0,accelerationinitshort=0,accelerationshort=0,accelerationmaxshort=0))
            return endf
        if enrich == 'sma':
            endf.insert(0,column='sma',value=ta.SMA(endf['close'],timeperiod=30))
            return endf
        if enrich == 't3':
            endf.insert(0,column='t3',value=ta.T3(endf['close'],timeperiod=5,vfactor=0)) # Unstable period
            return endf
        if enrich == 'tema':
            endf.insert(0,column='tema',value=ta.TEMA(endf['close'],timeperiod=30))
            return endf
        if enrich == 'trima':
            endf.insert(0,column='trima',value=ta.TRIMA(endf['close'],timeperiod=30))
            return endf
        if enrich == 'wma':
            endf.insert(0,column='wma',value=ta.WMA(endf['close'],timeperiod=30))
            return endf

        # Momentum
        if enrich == 'adx':
            endf.insert(0,column='adx',value=ta.ADX(endf['high'],endf['low'],endf['close'],timeperiod=14))
            return endf
        if enrich == 'adxr':
            endf.insert(0,column='adxr',value=ta.ADXR(endf['high'],endf['low'],endf['close'],timeperiod=14))
            return endf
        if enrich == 'apo':
            endf.insert(0,column='apo',value=ta.APO(endf['close'],fastperiod=12, slowperiod=26, matype=0))
            return endf
        if enrich == 'aroonosc':
            endf.insert(0,column='aroonosc',value=ta.AROONOSC(endf['high'],endf['low'],timeperiod=14))
            return endf
        if enrich == 'aroon':
            aroondown, aroonup = ta.AROON(endf['high'],endf['low'],timeperiod=14)
            endf.insert(0,column='aroonup',value=aroonup)
            endf.insert(0,column='aroondown',value=aroondown)
            return endf
        if enrich == 'bop':
            endf.insert(0,column='bop',value=ta.BOP(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cci':
            endf.insert(0,column='cci',value=ta.CCI(endf['high'],endf['low'],endf['close'],timeperiod=14))
            return endf
        if enrich == 'cmo':
            endf.insert(0,column='cmo',value=ta.CMO(endf['close'],timeperiod=14))
            return endf
        if enrich == 'dx':
            endf.insert(0,column='dx',value=ta.DX(endf['high'],endf['low'],endf['close'],timeperiod=14))
            return endf
        if enrich == 'macd':
            macd, macdsignal, macdhist = ta.MACD(endf['close'], fastperiod=12, slowperiod=26, signalperiod=9)
            endf.insert(0,column='macd',value=macd)
            endf.insert(0,column='macdsignal',value=macdsignal)
            endf.insert(0,column='macdhist',value=macdhist)
            return endf
        if enrich == 'mfi':
            endf.insert(0,column='mfi',value=ta.MFI(endf['high'],endf['low'],endf['close'],endf['volume'],timeperiod=14))
            return endf
        if enrich == 'mom':
            endf.insert(0,column='mom',value=ta.MOM(endf['close'],timeperiod=10))
            return endf
        if enrich == 'ppo':
            endf.insert(0,column='ppo',value=ta.PPO(endf['close'],fastperiod=12, slowperiod=26, matype=0))
            return endf
        if enrich == 'roc':
            endf.insert(0,column='roc',value=ta.ROC(endf['close'],timeperiod=10))
            return endf
        if enrich == 'rocp':
            endf.insert(0,column='rocp',value=ta.ROCP(endf['close'],timeperiod=10))
            return endf
        if enrich == 'rsi':
            endf.insert(0,column='rsi',value=ta.RSI(endf['close'],timeperiod=14))
            return endf
        if enrich == 'stoch':
            slowk, slowd = ta.STOCH(endf['high'], endf['low'], endf['close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
            endf.insert(0,column='slowk',value=slowk)
            endf.insert(0,column='slowd',value=slowd)
            return endf
        if enrich == 'trix':
            endf.insert(0,column='trix',value=ta.TRIX(endf['close'],timeperiod=30))
            return endf
        if enrich == 'ultosc':
            endf.insert(0,column='ultosc',value=ta.ULTOSC(endf['high'],endf['low'],endf['close'],timeperiod1=7, timeperiod2=14, timeperiod3=28))
            return endf
        if enrich == 'willr':
            endf.insert(0,column='willr',value=ta.WILLR(endf['high'],endf['low'],endf['close'],timeperiod=14))
            return endf

        # Volume
        if enrich == 'ad':
            endf.insert(0,column='ad',value=ta.AD(endf['high'],endf['low'],endf['close'],endf['volume']))
            return endf
        if enrich == 'adosc':
            endf.insert(0,column='adosc',value=ta.ADOSC(endf['high'],endf['low'],endf['close'],endf['volume'],fastperiod=3, slowperiod=10))
            return endf
        if enrich == 'obv':
            endf.insert(0,column='obv',value=ta.OBV(endf['close'],endf['volume']))
            return endf

        # Volitility
        if enrich == 'atr':
            endf.insert(0,column='atr',value=ta.ATR(endf['high'],endf['low'],endf['close'],timeperiod=14))
            return endf
        if enrich == 'natr':
            endf.insert(0,column='natr',value=ta.NATR(endf['high'],endf['low'],endf['close'],timeperiod=14))
            return endf
        if enrich == 'trange':
            endf.insert(0,column='trange',value=ta.TRANGE(endf['high'],endf['low'],endf['close']))
            return endf

        # Pattern
        if enrich == 'cdl2crows':
            endf.insert(0,column='cdl2crows',value=ta.CDL2CROWS(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdl3blackcrows':
            endf.insert(0,column='cdl3blackcrows',value=ta.CDL3BLACKCROWS(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdl3inside':
            endf.insert(0,column='cdl3inside',value=ta.CDL3INSIDE(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdl3linestrike':
            endf.insert(0,column='cdl3linestrike',value=ta.CDL3LINESTRIKE(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdl3outside':
            endf.insert(0,column='cdlcdl3outside',value=ta.CDL3OUTSIDE(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdl3starsinsouth':
            endf.insert(0,column='cdl3starsinsouth',value=ta.CDL3STARSINSOUTH(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdl3whitesoldiers':
            endf.insert(0,column='cdl3whitesoldiers',value=ta.CDL3WHITESOLDIERS(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlabandonedbaby':
            endf.insert(0,column='cdlabandonedbaby',value=ta.CDLABANDONEDBABY(endf['open'],endf['high'],endf['low'],endf['close'],penetration=0))
            return endf
        if enrich == 'cdladvanceblock':
            endf.insert(0,column='cdladvanceblock',value=ta.CDLADVANCEBLOCK(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlbelthold':
            endf.insert(0,column='cdlbelthold',value=ta.CDLBELTHOLD(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlbreakaway':
            endf.insert(0,column='cdlbreakaway',value=ta.CDLBREAKAWAY(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlclosingmarubozu':
            endf.insert(0,column='cdlclosingmarubozu',value=ta.CDLCLOSINGMARUBOZU(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlconcealbabyswall':
            endf.insert(0,column='cdlconcealbabyswall',value=ta.CDLCONCEALBABYSWALL(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlcounterattack':
            endf.insert(0,column='cdlcounterattack',value=ta.CDLCOUNTERATTACK(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdldarkcloudcover':
            endf.insert(0,column='cdldarkcloudcover',value=ta.CDLDARKCLOUDCOVER(endf['open'],endf['high'],endf['low'],endf['close'],penetration=0))
            return endf
        if enrich == 'cdldoji':
            endf.insert(0,column='cdldoji',value=ta.CDLDOJI(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdldojistar':
            endf.insert(0,column='cdldojistar',value=ta.CDLDOJISTAR(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdldragonflydoji':
            endf.insert(0,column='cdldragonflydoji',value=ta.CDLDRAGONFLYDOJI(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlengulfing':
            endf.insert(0,column='cdlengulfing',value=ta.CDLENGULFING(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdleveningdojistar':
            endf.insert(0,column='cdleveningdojistar',value=ta.CDLEVENINGDOJISTAR(endf['open'],endf['high'],endf['low'],endf['close'],penetration=0))
            return endf
        if enrich == 'cdleveningstar':
            endf.insert(0,column='cdleveningstar',value=ta.CDLEVENINGSTAR(endf['open'],endf['high'],endf['low'],endf['close'],penetration=0))
            return endf
        if enrich == 'cdlgapsidesidewhite':
            endf.insert(0,column='cdlgapsidesidewhite',value=ta.CDLGAPSIDESIDEWHITE(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlgravestonedoji':
            endf.insert(0,column='cdlgravestonedoji',value=ta.CDLGRAVESTONEDOJI(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlhammer':
            endf.insert(0,column='cdlhammer',value=ta.CDLHAMMER(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlhangingman':
            endf.insert(0,column='cdlhangingman',value=ta.CDLHANGINGMAN(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlharami':
            endf.insert(0,column='cdlharami',value=ta.CDLHARAMI(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlharamicross':
            endf.insert(0,column='cdlharamicross',value=ta.CDLHARAMICROSS(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlhighwave':
            endf.insert(0,column='cdlhighwave',value=ta.CDLHIGHWAVE(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlhikkake':
            endf.insert(0,column='cdlhikkake',value=ta.CDLHIKKAKE(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlhikkakemod':
            endf.insert(0,column='cdlhikkakemod',value=ta.CDLHIKKAKEMOD(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlhomingpigeon':
            endf.insert(0,column='cdlhomingpigeon',value=ta.CDLHOMINGPIGEON(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlidentical3crows':
            endf.insert(0,column='cdlidentical3crows',value=ta.CDLIDENTICAL3CROWS(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlinneck':
            endf.insert(0,column='cdlinneck',value=ta.CDLINNECK(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlinvertedhammer':
            endf.insert(0,column='cdlinvertedhammer',value=ta.CDLINVERTEDHAMMER(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlkicking':
            endf.insert(0,column='cdlkicking',value=ta.CDLKICKING(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlkickingbylength':
            endf.insert(0,column='cdlkickingbylength',value=ta.CDLKICKINGBYLENGTH(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlladderbottom':
            endf.insert(0,column='cdlladderbottom',value=ta.CDLLADDERBOTTOM(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdllongleggeddoji':
            endf.insert(0,column='cdllongleggeddoji',value=ta.CDLLONGLEGGEDDOJI(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdllongline':
            endf.insert(0,column='cdllongline',value=ta.CDLLONGLINE(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlmarubozu':
            endf.insert(0,column='cdlmarubozu',value=ta.CDLMARUBOZU(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlmatchinglow':
            endf.insert(0,column='cdlmatchinglow',value=ta.CDLMATCHINGLOW(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlmathold':
            endf.insert(0,column='cdlmathold',value=ta.CDLMATHOLD(endf['open'],endf['high'],endf['low'],endf['close'],penetration=0))
            return endf
        if enrich == 'cdlmorningdojistar':
            endf.insert(0,column='cdlmorningdojistar',value=ta.CDLMORNINGDOJISTAR(endf['open'],endf['high'],endf['low'],endf['close'],penetration=0))
            return endf
        if enrich == 'cdlmorningstar':
            endf.insert(0,column='cdlmorningstar',value=ta.CDLMORNINGSTAR(endf['open'],endf['high'],endf['low'],endf['close'],penetration=0))
            return endf
        if enrich == 'cdlonneck':
            endf.insert(0,column='cdlonneck',value=ta.CDLONNECK(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlpiercing':
            endf.insert(0,column='cdlpiercing',value=ta.CDLPIERCING(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlrickshawman':
            endf.insert(0,column='cdlrickshawman',value=ta.CDLRICKSHAWMAN(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlrisefall3methods':
            endf.insert(0,column='cdlrisefall3methods',value=ta.CDLRISEFALL3METHODS(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlseparatinglines':
            endf.insert(0,column='cdlseparatinglines',value=ta.CDLSEPARATINGLINES(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlshootingstar':
            endf.insert(0,column='cdlshootingstar',value=ta.CDLSHOOTINGSTAR(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlshortline':
            endf.insert(0,column='cdlshortline',value=ta.CDLSHORTLINE(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlspinningtop':
            endf.insert(0,column='cdlspinningtop',value=ta.CDLSPINNINGTOP(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlstalledpattern':
            endf.insert(0,column='cdlstalledpattern',value=ta.CDLSTALLEDPATTERN(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlsticksandwich':
            endf.insert(0,column='cdlsticksandwich',value=ta.CDLSTICKSANDWICH(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdltakuri':
            endf.insert(0,column='cdltakuri',value=ta.CDLTAKURI(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdltasukigap':
            endf.insert(0,column='cdltasukigap',value=ta.CDLTASUKIGAP(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlthrusting':
            endf.insert(0,column='cdlthrusting',value=ta.CDLTHRUSTING(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdltristar':
            endf.insert(0,column='cdltristar',value=ta.CDLTRISTAR(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlunique3river':
            endf.insert(0,column='cdlunique3river',value=ta.CDLUNIQUE3RIVER(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlupsidegap2crows':
            endf.insert(0,column='cdlupsidegap2crows',value=ta.CDLUPSIDEGAP2CROWS(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'cdlxsidegap3methods':
            endf.insert(0,column='cdlxsidegap3methods',value=ta.CDLXSIDEGAP3METHODS(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf

        # Price
        if enrich == 'avgprice':
            endf.insert(0,column='avgprice',value=ta.AVGPRICE(endf['open'],endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'medprice':
            endf.insert(0,column='medprice',value=ta.MEDPRICE(endf['high'],endf['low']))
            return endf
        if enrich == 'typprice':
            endf.insert(0,column='typprice',value=ta.TYPPRICE(endf['high'],endf['low'],endf['close']))
            return endf
        if enrich == 'wclprice':
            endf.insert(0,column='wclprice',value=ta.WCLPRICE(endf['high'],endf['low'],endf['close']))
            return endf

        # Stats
        if enrich == 'beta':
            endf.insert(0,column='beta',value=ta.BETA(endf['high'],endf['low'],timeperiod=5))
            return endf
        if enrich == 'correl':
            endf.insert(0,column='correl',value=ta.CORREL(endf['high'],endf['low'],timeperiod=30))
            return endf
        if enrich == 'linearreg':
            endf.insert(0,column='linearreg',value=ta.LINEARREG(endf['close'],timeperiod=14))
            return endf
        if enrich == 'linearreg_angle':
            endf.insert(0,column='linearreg_angle',value=ta.LINEARREG_ANGLE(endf['close'],timeperiod=14))
            return endf
        if enrich == 'linearreg_intercept':
            endf.insert(0,column='linearreg_intercept',value=ta.LINEARREG_INTERCEPT(endf['close'],timeperiod=14))
            return endf
        if enrich == 'linearreg_slope':
            endf.insert(0,column='linearreg_slope',value=ta.LINEARREG_SLOPE(endf['close'],timeperiod=14))
            return endf
        if enrich == 'stddev':
            endf.insert(0,column='stddev',value=ta.STDDEV(endf['close'],timeperiod=5,nbdev=1))
            return endf
        if enrich == 'tsf':
            endf.insert(0,column='tsf',value=ta.TSF(endf['close'],timeperiod=14))
            return endf
        if enrich == 'var':
            endf.insert(0,column='var',value=ta.VAR(endf['close'],timeperiod=5,nbdev=1))
            return endf

    def listDepen(self):
        depen = {'nana':'None',
                '1BarClose':'One Bar Ahead',
                '2BarClose':'Two Bars Ahead',
                '3BarClose':'Three Bars Ahead',
                '1BarBool':'One Bar Ahead Bool',
                '2BarBool':'Two Bars Ahead Bool',
                '3BarBool':'Three Bars Ahead Bool',
                'High5':'High 5 peaks Bool',
                'Low5':'Low 5 dips Bool',
                'High10':'High 10 peaks Bool',
                'Low10':'Low 10 dips Bool'}
        return depen

    def addDepen(self,enrich,endf):
        if enrich == 'nana':
            endf['dependef'] = endf['close']
            return endf
        if enrich == '1BarClose':
            endf.insert(endf.shape[1],column='depen1',value=(endf.diff(periods=-1)['close']*-1))
            return endf
        if enrich == '2BarClose':
            endf.insert(endf.shape[1],column='depen2',value=(endf.diff(periods=-2)['close']*-1))
            return endf
        if enrich == '3BarClose':
            endf.insert(endf.shape[1],column='depen3',value=(endf.diff(periods=-3)['close']*-1))
            return endf

        if enrich == '1BarBool':
            # Diff comes back with negative showing positive change
            endf.loc[endf.diff(periods=-1)['close']<0,'depen1bool'] = 1
            endf.loc[endf.diff(periods=-1)['close']>=0,'depen1bool'] = 0
            return endf
        if enrich == '2BarBool':
            # Diff comes back with negative showing positive change
            endf.loc[endf.diff(periods=-2)['close']<0,'depen2bool'] = 1
            endf.loc[endf.diff(periods=-2)['close']>=0,'depen2bool'] = 0
            return endf
        if enrich == '3BarBool':
            # Diff comes back with negative showing positive change
            endf.loc[endf.diff(periods=-3)['close']<0,'depen3bool'] = 1
            endf.loc[endf.diff(periods=-3)['close']>=0,'depen3bool'] = 0
            return endf

        if enrich == 'High5':
            n=5 # number of points to be checked before and after
            endf['High5'] = endf.iloc[argrelextrema(endf.high.values, np.greater_equal, order=n)[0]]['high']
            endf['High5'].fillna(0, inplace=True)
            endf.loc[endf['High5']>0,'High5'] = 1
            return endf
        if enrich == 'Low5':
            n=5 # number of points to be checked before and after
            endf['Low5'] = endf.iloc[argrelextrema(endf.low.values, np.less_equal, order=n)[0]]['low']
            endf['Low5'].fillna(0, inplace=True)
            endf.loc[endf['Low5']>0,'Low5'] = 1
            return endf

        if enrich == 'High10':
            n=10 # number of points to be checked before and after
            endf['High10'] = endf.iloc[argrelextrema(endf.high.values, np.greater_equal, order=n)[0]]['high']
            endf['High10'].fillna(0, inplace=True)
            endf.loc[endf['High10']>0,'High10'] = 1
            return endf
        if enrich == 'Low10':
            n=10 # number of points to be checked before and after
            endf['Low10'] = endf.iloc[argrelextrema(endf.low.values, np.less_equal, order=n)[0]]['low']
            endf['Low10'].fillna(0, inplace=True)
            endf.loc[endf['Low10']>0,'Low10'] = 1
            return endf

    def listNaN(self):
        nanas = {'drop':'Drop rows',
                'fzero':'Fill with Zeros',
                'ffill':'Forward Fill',
                'bfill':'Back Fill',
                'non':'None'}
        return nanas

    def doNaN(self, nana, nadf):
        if nana == 'non':
            # Do nothing return full Dataframe
            return nadf

        if nana == 'drop':
            # Drop any NaN row
            nadf.dropna(inplace=True)
            # Reset indexes as feather is touchy
            nadf.reset_index(drop=True, inplace=True)
            return nadf

        if nana == 'fzero':
            return nadf.fillna(0)
        if nana == 'ffill':
            return nadf.fillna(method='ffill')
        if nana == 'bfill':
            return nadf.fillna(method='bfill')
