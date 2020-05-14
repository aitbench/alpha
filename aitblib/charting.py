# Import base class
from .basic import Basic
# Standard imports
import pandas as pd
# import sys
# Bokeh imports
from bokeh.layouts import gridplot
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.io import curdoc
from bokeh.models import BasicTicker, ColorBar, LinearColorMapper, ColumnDataSource
from bokeh.transform import transform
from bokeh.palettes import Viridis256
# import matplotlib as mpl
from math import pi
# ML stuffs for Feature Selection
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import ExtraTreesClassifier


class Chart(Basic):

    def viewNugget(self, nugget):
        # Read Nugget to DataFrame
        nfile = self.nuggetDataPath + nugget + '.feather'
        df = pd.read_feather(nfile)
        # Get info from Nugget filename
        info = self.nugInfo(nfile)
        w = self.tfToMS(info['timeframe'])
        # Attach theme to current document
        curdoc().theme = self.bokehTheme  # light_minimal dark_minimal
        # Init plots
        plots = []
        # OHLC plot
        # Create array of incremental and decremental candles
        inc = df.Close > df.Open
        dec = df.Open > df.Close
        # Create title from nugget info
        title = info['symb'] + ' ' + info['timeframe'] + ' From:' + info['from'] + ' To:' + info['to']
        # Create first figure of OHLC
        TOOLS = "pan,wheel_zoom,reset,save"
        p = figure(x_axis_type="datetime", sizing_mode='scale_width', tools=TOOLS, height=200, title=title)
        p.grid.grid_line_alpha = 0.3
        p.segment(df.Date, df.High, df.Date, df.Low, color="black")
        # Add in
        p.vbar(df.Date[inc], w, df.Open[inc], df.Close[inc], fill_color="#D5E1DD", line_color="black")
        p.vbar(df.Date[dec], w, df.Open[dec], df.Close[dec], fill_color="#F2583E", line_color="black")
        plots.append(p)
        # Dependant plot
        i = figure(x_axis_type="datetime", sizing_mode='scale_width', x_range=p.x_range, height=50, title=df.columns[-1])
        i.square(df.Date, df.iloc[:, -1])
        plots.append(i)
        # Additional independants plot
        for col in df.columns[:-7]:
            d = figure(x_axis_type="datetime", sizing_mode='scale_width', x_range=p.x_range, height=50, title=col)
            d.line(df.Date, df[col])
            plots.append(d)
        # Create Bokeh Grid
        grid = gridplot(plots, ncols=1, sizing_mode='scale_width', toolbar_location="right")
        # Return components in the following form
        # script, div = components(grid)
        return components(grid)

    def viewCorr(self, nugget):
        # Read Nugget to DataFrame
        nfile = self.nuggetDataPath + nugget + '.feather'
        df = pd.read_feather(nfile)
        # Get info from Nugget filename
        info = self.nugInfo(nfile)
        # Attach theme to current document
        curdoc().theme = self.bokehTheme  # light_minimal dark_minimal
        # Now we will create correlation matrix using pandas
        df = df.iloc[:, 0:-7]
        df = df.corr()
        # Rename index and columns
        df.index.name = 'AllColumns1'
        df.columns.name = 'AllColumns2'
        # Prepare data.frame in the right format
        df = df.stack().rename("value").reset_index()
        # You can use your own palette here
        # colors = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']
        # I am using 'Viridis256' to map colors with value, change it with 'colors' if you need some specific colors
        mapper = LinearColorMapper(
            palette=Viridis256, low=df.value.min(), high=df.value.max())
        # Define a figure and tools
        TOOLS = "pan,wheel_zoom,box_zoom,reset"
        p = figure(
            tools=TOOLS,
            sizing_mode='scale_width',
            title="Correlation plot of " + info['symb'] + ' ' + info['timeframe'],
            x_range=list(df.AllColumns1.drop_duplicates()),
            y_range=list(df.AllColumns2.drop_duplicates()),
            toolbar_location="right",
            x_axis_location="below")
        # Create rectangle for heatmap
        p.rect(
            x="AllColumns1",
            y="AllColumns2",
            width=1,
            height=1,
            source=ColumnDataSource(df),
            line_color=None,
            fill_color=transform('value', mapper))
        # Add legend
        color_bar = ColorBar(
            color_mapper=mapper,
            location=(0, 0),
            ticker=BasicTicker(desired_num_ticks=10))
        p.xaxis.major_label_orientation = pi / 4
        p.add_layout(color_bar, 'right')
        return components(p)

    def viewFeat(self, nugget):
        # Read Nugget to DataFrame
        nfile = self.nuggetDataPath + nugget + '.feather'
        df = pd.read_feather(nfile)
        # Get info from Nugget filename
        info = self.nugInfo(nfile)
        # Attach theme to current document
        curdoc().theme = self.bokehTheme  # light_minimal dark_minimal
        # Get XTree Classficiation
        xTree = self.exClass(df)
        xFrame = xTree.to_frame()
        # Create XTree plot
        x = figure(x_range=xFrame.index.values, plot_height=100, title="XTree Classifier Feature Importance on " + info['depen'])
        x.vbar(x=xFrame.index.values, top=xFrame[0], width=0.9)
        x.xgrid.grid_line_color = None
        x.y_range.start = 0
        # Get KClass Classification
        kC = self.kClass(df)
        # Plot K figure
        k = figure(x_range=kC.Specs, plot_height=100, title="KClass Feature Selection on " + info['depen'])
        k.vbar(x=kC.Specs, top=kC.Score, width=0.9)
        k.xgrid.grid_line_color = None
        k.y_range.start = 0
        # Create Bokeh Grid
        grid = gridplot([k, x], ncols=1, sizing_mode='scale_width', toolbar_location="right")
        # Return components in the following form
        return components(grid)

    def kClass(self, data):
        X = data.iloc[:, 0:len(data.columns) - 7]
        y = data.iloc[:, -1]
        # Capture column names before Scaler kills them
        dfcolumns = pd.DataFrame(X.columns)
        # Scale
        X = MinMaxScaler().fit_transform(X)
        # y = MinMaxScaler().fit_transform(y)
        # apply SelectKBest class to extract top 10 best features
        bestfeatures = SelectKBest(score_func=chi2, k='all')
        fit = bestfeatures.fit(X, y)
        dfscores = pd.DataFrame(fit.scores_)
        # concat two dataframes for better visualization
        featureScores = pd.concat([dfcolumns, dfscores], axis=1)
        featureScores.columns = ['Specs', 'Score']
        return featureScores.nlargest(10, 'Score')

    def exClass(self, data):
        X = data.iloc[:, 0:-7]
        y = data.iloc[:, -1]
        # Trees
        model = ExtraTreesClassifier()
        model.fit(X, y)
        # use inbuilt class feature_importances of tree based classifiers
        # plot graph of feature importances for better visualization
        feat_importances = pd.Series(model.feature_importances_, index=X.columns)
        return feat_importances.nlargest(10)
