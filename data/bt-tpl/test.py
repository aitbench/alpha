import os
# Delete following line if you wish to use CUDA
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import pandas as pd
import pickle as pkl
from datetime import datetime
from backtesting import Backtest, Strategy
import quantstats as qs

class XXXNAMEXXX(Strategy):
    # Any variables in here can be used for optimization
    SL = XXXSTOPLOSSXXX
    TP = XXXTAKEPROFITXXX

    def init(self):
        super().init()
        # StopLoss and TakeProfit
        self.sl = 1 - (0.01 * self.SL)
        self.tp = 1 + (0.01 * self.TP)
        # Pull Native DF
        self.mydf = self.data.getDF
        ## AI Setup
        # Load Entry DF
        import pickle as pkl
        self.endf = pkl.load(open('XXXENDFXXX', 'rb'))
        # Load the scaler
        self.ensclr = pkl.load(open('XXXENTSCLRXXX', 'rb'))
        # Load the model
        import keras
        # Keras threading fix - DO NOT REMOVE :P
        import keras.backend.tensorflow_backend as tb
        tb._SYMBOLIC_SCOPE.value = True
        self.enmodel = keras.models.load_model('XXXENTMODELXXX')

    def next(self):
        super().next()
        idx = self.data.index[-1]
        price = self.data.Close[-1]

        highest = 0
        lowest = 9999999999
        for x in range(-1,-40,-1):
            if self.data.Low[x] < lowest:
                lowest = self.data.Low[x]
            if self.data.High[x] > highest:
                highest = self.data.High[x]

        print("Lowest",lowest)
        print("Highest",highest)

        diff = highest - lowest
        entdiff = lowest + (0.01*self.entPerc)*diff

        # Test AI with values at idx
        if self.predEnt(idx):
            # Buy if not in a current position
            if not self.position:
                self.buy(sl=self.sl*price, tp=self.tp*price)

        # Print equity to show progress
        #print(self.equity)

    # Prediction entry from model
    def predEnt(self,idx):
        # Get independants at idx
        X = self.endf.loc[idx].values[0:-6]
        # Reshape ndarray for Scaler
        import numpy as np
        X = np.reshape(X,(1,-1))
        # Transform via preloaded scaler
        XScaled = self.ensclr.transform(X)
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

# Quantstats report https://github.com/ranaroussi/quantstats
# Create up Buy and Hold returns
hodler = natdf['Close'].tail(max).pct_change()
qs.reports.html(bt.stdf['Returns'], hodler, output='Report.html')

# Plot the graph with all the shinies. 60k bars seem to be a limit with everything else turned on
bt.plot()
