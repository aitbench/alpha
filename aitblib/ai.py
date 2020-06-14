import os
import datetime
import sys
import yaml
import pandas as pd
import pickle as pkl
# AITB Basic base class
from .basic import Basic
# Needed for training NNs
from sklearn.model_selection import train_test_split
# Importing the Keras libraries and packages
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import CSVLogger
# Decimal needed for Decimal :P
from decimal import Decimal
# Accuracy and Loss Plots
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


class AI(Basic):

    def test(self):
        # Create lock file
        tname = self.logPath + 'aitest.log'
        with open(tname, 'a') as file:
            file.write(str(datetime.datetime.now()) + " -- AI Testing timing and threads\n")
        print('AIRunner', file=sys.stderr)

    def trainANN(self):
        # Fuckit might work and it does. DO NOT REMOVE :P
        import keras.backend.tensorflow_backend as tb
        tb._SYMBOLIC_SCOPE.value = True
        # CPU Only Comment out to use GPU, CPU was faster for me
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        # Setup Logs and runner
        tname = self.runPath + 'trainANN.run'
        tlog = self.logPath + 'trainANN.log'
        # Test if already running
        if os.path.exists(tname):
            return
        # Write lock file
        with open(tname, 'w') as file:
            file.write(str(datetime.datetime.now()))
        # Get list of data files
        annCfgs = self.listCfgFiles('aiann')
        for file in annCfgs:
            aConf = self.readCfgFile('aiann', file)
            if aConf['training']:
                # Read Nugget to DataFrame
                nfile = self.nuggetDataPath + aConf['nugget'] + '.pkl'
                df = pd.read_pickle(nfile)
                # Starting log entry
                with open(tlog, 'w+') as file:
                    file.write(str(datetime.datetime.now()) + " -- Training " + aConf['id'] + " ...\n")
                # Check scarcity
                if aConf['scarcity']:
                    with open(tlog, 'a+') as file:
                        file.write(str(datetime.datetime.now()) + " -- Starting Scarcity measures...\n")
                    sfile = self.annDataPath + aConf['id'] + '_sorted.pkl'
                    if os.path.exists(sfile):
                        with open(sfile, 'rb') as fin:
                            df = pkl.load(fin)
                    else:
                        depen = aConf['depen']
                        # Itterate to find positives
                        county = 0
                        posdf = pd.DataFrame(columns=df.columns)
                        for row in range(len(df)):
                            if df[depen].iloc[row] > 0:
                                county += 1
                                posdf = posdf.append(df.iloc[row], ignore_index=True)
                        with open(tlog, 'a+') as file:
                            file.write(str(datetime.datetime.now()) + " -- Number of Positive Dependants: " + str(county) + "\n")
                        with open(tlog, 'a+') as file:
                            file.write(str(datetime.datetime.now()) + " -- Number of Total Rows in Dataset: " + str(len(df)) + "\n")
                        # Create percentage
                        TWOPLACES = Decimal(10) ** -2
                        perc = Decimal((county / len(df)) * 100).quantize(TWOPLACES)
                        with open(tlog, 'a+') as file:
                            file.write(str(datetime.datetime.now()) + " -- Percentage of Positives: " + str(perc) + "%" + "\n")
                        # Itterate to find negatives in reverse order on DF
                        posit = 0
                        negdf = pd.DataFrame(columns=df.columns)
                        for row in range(len(df) - 1, 0, -1):
                            self.ll(df.index[row])
                            if df[depen].iloc[row] == 0:
                                posit += 1
                                negdf = negdf.append(df.iloc[row], ignore_index=True)
                            if posit > (1.25 * county):
                                break
                        # Create final dataframe choosing from each side
                        fidf = pd.DataFrame(columns=df.columns)
                        for row in range(len(posdf)):
                            fidf = fidf.append(posdf.iloc[row], ignore_index=True)
                            fidf = fidf.append(negdf.iloc[row], ignore_index=True)
                        # Flip df to new slotted DF
                        df = fidf
                        with open(tlog, 'a+') as file:
                            file.write(str(datetime.datetime.now()) + " -- Number of Positive Dependants: " + str(county) + "\n")
                        with open(tlog, 'a+') as file:
                            file.write(str(datetime.datetime.now()) + " -- Number of Total Rows in Dataset: " + str(len(df)) + "\n")
                        # Create percentage
                        perc = Decimal((county / len(df)) * 100).quantize(TWOPLACES)
                        with open(tlog, 'a+') as file:
                            file.write(str(datetime.datetime.now()) + " -- Percentage of Positives: " + str(perc) + "%" + "\n")

                        # Save Sorted file
                        with open(sfile, 'wb') as fout:
                            pkl.dump(df, fout)

                        # Scarcity finalization
                        with open(tlog, 'a+') as file:
                            file.write(str(datetime.datetime.now()) + " -- Scarcity Finalized \n")

                # Create Independants X and Dependant y series
                X = df.iloc[:, 0:-6].values
                y = df.iloc[:, -1].values
                # Splitting the dataset into the Training set and Test set
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=aConf['testsplit'], random_state=0)
                # Select Scaler
                if aConf['scaler'] == "standard":
                    from sklearn.preprocessing import StandardScaler
                    sc = StandardScaler()
                if aConf['scaler'] == "minmax":
                    from sklearn.preprocessing import MinMaxScaler
                    sc = MinMaxScaler()
                if aConf['scaler'] == "maxabs":
                    from sklearn.preprocessing import MinAbsScaler
                    sc = MinAbsScaler()
                if aConf['scaler'] == "robust":
                    from sklearn.preprocessing import RobustScaler
                    sc = RobustScaler()
                if aConf['scaler'] == "poweryeo":
                    from sklearn.preprocessing import PowerTransformer
                    sc = PowerTransformer(method='yeo-johnson')
                if aConf['scaler'] == "powerbox":
                    from sklearn.preprocessing import PowerTransformer
                    sc = PowerTransformer(method='box-cox')
                if aConf['scaler'] == "quantgauss":
                    from sklearn.preprocessing import QuantileTransformer
                    sc = QuantileTransformer(output_distribution='normal')
                if aConf['scaler'] == "quantuni":
                    from sklearn.preprocessing import QuantileTransformer
                    sc = QuantileTransformer(output_distribution='uniform')
                if aConf['scaler'] == "normalizer":
                    from sklearn.preprocessing import Normalizer
                    sc = Normalizer()

                # Scale variables
                X_train = sc.fit_transform(X_train)
                X_test = sc.transform(X_test)

                # Dump Scaler to Pickle
                with open(self.annDataPath + aConf['id'] + '.pkl', 'wb') as fout:
                    pkl.dump(sc, fout)

                # Get dynamic sizes from amount of independants
                inSize = X.shape[1]
                # numUnits = round((inSize + 1)/2) # Suggested unitsize

                # Initialising the ANN
                classifier = Sequential()
                # Adding the input layer
                classifier.add(Dense(units=aConf['inputlayerunits'], kernel_initializer='uniform', activation='relu', input_dim=inSize))
                # Adding hidden layers
                for i in range(aConf['hiddenlayers']):
                    classifier.add(Dense(units=aConf['hiddenlayerunits'], kernel_initializer='uniform', activation='relu'))
                # Adding the output layer
                classifier.add(Dense(units=1, kernel_initializer='uniform', activation='sigmoid'))
                # Compiling the ANN
                classifier.compile(optimizer=aConf['optimizer'], loss=aConf['loss'], metrics=[aConf['metrics']])
                # Setup logger
                csv_logger = CSVLogger(tlog, append=True)
                # Fitting the ANN to the Training set
                history = classifier.fit(X_train, y_train, validation_data=(X_test, y_test), batch_size=aConf['batchsize'], epochs=aConf['epoch'], callbacks=[csv_logger])
                # , verbose=0
                # Save the model
                classifier.save(self.annDataPath + aConf['id'] + '.tf')

                # Accuracy
                aConf['testaccuracy'] = str(round(history.history['val_accuracy'][-1], 2))
                aConf['trainaccuracy'] = str(round(history.history['accuracy'][-1], 2))

                # Wipe previous files as they do not overwrite
                lChart = self.chartPath + aConf['id'] + '_loss.png'
                if os.path.exists(lChart):
                    os.remove(lChart)
                # Plot Loss
                plt.title('Loss')
                plt.plot(history.history['loss'], label='train')
                plt.plot(history.history['val_loss'], label='test')
                plt.legend()
                plt.savefig(lChart, pad_inches=0.01, dpi=60)
                plt.close()

                # Wipe previous files as they do not overwrite
                aChart = self.chartPath + aConf['id'] + '_acc.png'
                if os.path.exists(aChart):
                    os.remove(aChart)
                # Plot Accuracy
                plt.title('Accuracy')
                plt.plot(history.history['accuracy'], label='train')
                plt.plot(history.history['val_accuracy'], label='test')
                plt.legend()
                plt.savefig(aChart, pad_inches=0.01, dpi=90)
                plt.close()

                # Remove training and add timestamp
                aConf['lasttrain'] = str(datetime.datetime.now())
                aConf['training'] = False

                # Save config
                aYML = yaml.dump(aConf, default_flow_style=False, sort_keys=False)
                # print(aYML,file=sys.stderr)
                self.writeCfgFile('aiann', aConf['id'], aYML)
        # Remove File Lock
        os.remove(tname)
