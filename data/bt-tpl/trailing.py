import os
# Delete following line if you wish to use CUDA
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import pandas as pd
import pickle as pkl
from datetime import datetime
from backtesting import Backtest, Strategy
from backtesting.lib import TrailingStrategy
import quantstats as qs

class XXXNAMEXXX(TrailingStrategy):
    # Any variables in here can be used for optimization
    SL = XXXSTOPLOSSXXX
    TATR = XXXTATRXXX
    TSL = XXXTSLXXX

    def init(self):
        super().init()
        # Imports
        import pickle as pkl
        import keras
        # Keras threading fix - DO NOT REMOVE :P
        import keras.backend.tensorflow_backend as tb
        tb._SYMBOLIC_SCOPE.value = True

        # StopLoss and TakeProfit
        self.slpc = 0.01 * self.SL * -1
        # Pull Native DF
        self.mydf = self.data.getDF

        ## AI Setup
        # Load Entry DF
        self.endf = pkl.load(open('XXXENDFXXX', 'rb'))
        # Load the scaler
        self.ensclr = pkl.load(open('XXXENTSCLRXXX', 'rb'))
        # Load the model
        self.enmodel = keras.models.load_model('XXXENTMODELXXX')

        ## Trailing Stuffs
        # def set_atr_periods(self, periods=100)
        # def set_trailing_sl(self, n_atr=6)
        self.set_atr_periods(self.TATR)
        self.set_trailing_sl(self.TSL)

    def next(self):
        super().next()
        idx = self.data.index[-1]
        price = self.data.Close[-1]

        # Test AI with values at idx
        if self.predEnt(idx) and not self.position:
            self.buy()

        # Print equity to show progress
        #print(self.equity)

        # Manual override of stoploss
        if self.position and self.position.pl_pct < self.slpc:
            self.position.close()

    # Prediction entry from model
    def predEnt(self,idx):
        # Get independants at idx
        enX = self.endf.loc[idx].values[0:-6]
        # Reshape ndarray for Scaler
        import numpy as np
        enX = np.reshape(enX,(1,-1))
        # Transform via preloaded scaler
        XScaled = self.ensclr.transform(enX)
        # Make raw and class predictions
        rawPred = self.enmodel.predict(XScaled)
        classPred = self.enmodel.predict_classes(XScaled)
        # Flip to boolean classPred flips at 0.5
        pred = (rawPred > 0.9)
        # Return prediction in boolean
        return pred

# Load dataframes
natdf = pkl.load(open('XXXNATDFXXX', 'rb'))
endf = pkl.load(open('XXXENDFXXX', 'rb'))

# Find max length of df
max = natdf.shape[0]
if max > endf.shape[0]:
    max = endf.shape[0]

# Create backtest based on df data
comm = XXXCOMMXXX * 0.01
bt = Backtest(natdf.tail(max), XXXNAMEXXX, cash=XXXCASHXXX, commission=comm, margin=XXXMARGINXXX)

# Run backtest sts are the returned stats
sts = bt.run()
sts.to_csv('XXXRESULTXXXX')

# Optimization based on Strategy class variables
# optstats = bt.optimize(TATR=range(12,108,12), TSL=range(1,12,1))
# print(optstats)

# Quantstats report https://github.com/ranaroussi/quantstats
# Create up Buy and Hold returns
hodler = natdf['Close'].tail(max).pct_change()
qs.reports.html(bt.stdf['Returns'], hodler, output='Report.html')

# Plot the graph with all the shinies. 60k bars seem to be a limit with everything else turned on
bt.plot()
