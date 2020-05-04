#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

# Flask stuffs
from flask import Flask, render_template, request, redirect, flash, jsonify, url_for, session
#from flask_debugtoolbar import DebugToolbarExtension
# SQL stuffs
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
# Logging for Flask
import logging
from logging import Formatter, FileHandler
# Flask Login manager
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# Flask AP Scheduler
from flask_apscheduler import APScheduler
# AI-TB
from aitblib.basic import Basic
from aitblib import helpers
from aitblib import runners
from aitblib import enrichments
from aitblib import charting
from aitblib.Flask_forms import *
# System
import os
import yaml
import ccxt
import datetime
import pandas as pd
# Testing only
import sys

# Remember these two
#print('This is error output', file=sys.stderr)
#print('This is standard output', file=sys.stdout)

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
#if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
# Init and config Flask
app = Flask(__name__)
app.config.from_pyfile('conf/flask.py')
app.config.from_pyfile('conf/db-default.py')

# Init and start Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Init SQLAlchemy
db = SQLAlchemy(app)

# Initialize SQLAlchemy Object
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
                        
# Add tables if not added
try:
    user = User.query.filter_by(email=email).first()
except:
    # No tables found set them up!
    db.create_all()
    print('Setting up Tables...',file=sys.stderr)

# This needs to be here for flask-login to work
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Overwrite weird url for redirect Do Not Remove
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

# Setup global variables
confPath = app.root_path+os.path.sep+'conf'+os.path.sep
dataPath = app.root_path+os.path.sep+'data'+os.path.sep

# Automatically tear down SQLAlchemy.
@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()
    #scheduler.shutdown()

# APScheduler
# Configuration Object
class ConfigAPS(object):
    SCHEDULER_API_ENABLED = True
# Init Scheduler
scheduler = APScheduler()
RunThe = runners.Runner(app.root_path,db)
# Test Job
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    @scheduler.task('interval', id='testjob', seconds=15)
    def testjob():
        RunThe.dataDownload(True)
    #Minute by minute
    @scheduler.task('cron', id='minutejob',  minute='*')
    def minutejob():
        # print('MinuteByMinute', file=sys.stdout)
        pass
    # Hourly
    # @scheduler.task('cron', id='hourlyjob', hour='*')
    # def hourlyjob():
    #     print('Hourly', file=sys.stdout)
    # # Daily
    # @scheduler.task('cron', id='dailyjob', day='*')
    # def dailyjob():
    #     print('Daily', file=sys.stdout)
    # # Weekly
    # @scheduler.task('cron', id='weeklyjob', week='*', day_of_week='sun')
    # def weeklyjob():
    #     print('Weekly', file=sys.stdout)

# Init Helper Class
do = helpers.Helper(app.root_path,db)
en = enrichments.Enrichment()
ch = charting.Chart(app.root_path,db)

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
@login_required
def home():
    # Create files lists for config files
    dataCounts = {'con': len(do.listCfgFiles('conn')),
                'data': len(do.listCfgFiles('data')),
                'samples': len(do.listDataFiles('samples')),
                'nuggets': len(do.listDataFiles('nuggets'))}
    # Render page
    return render_template('pages/home.html', dataCounts=dataCounts)

@app.route('/connections', methods=['GET', 'POST'])
@login_required
def connections():
    if request.method == 'POST':
        # Connection page wants something
        act = request.form['action']
        if act == 'add':
            # First page of adding Connection
            return render_template('pages/connections-add.html', action=act)
        if act == 'add2':
            # Second page of adding Connection
            mark = request.form['market']
            if mark == 'crypto':
                ex = ccxt.exchanges
                return render_template('pages/connections-add.html', action=act, market=mark, exch=ex, len = len(ex))
            if mark == 'forex':
                return render_template('pages/connections-add.html', action=act, market=mark)
        if act == 'fin':
            # Setup of exchange has finished create the connection
            ex = request.form['exchSel']
            market = request.form['market']
            if market == 'crypto':
                do.createCryptoCon(ex)
            return redirect("/connections")
        if act == 'info':
            # Create temp exchange instance based on post data
            ex = request.form['ex']
            return do.createCryptoInfo(ex)
        if act == 'fullinfo':
            con = request.form['con']
            # Create pathname and load connection config
            cfname = confPath+'conn'+os.path.sep+con+'.yml'
            with open(cfname,'r') as file:
                cfdata = yaml.full_load(file)
            # Create table in html
            cftable = "<table>"
            for key in cfdata:
                cftable = cftable+"<tr><th>"+str(key)+"</th><td>"+str(cfdata[key])+"</td></tr>"
            cftable = cftable+"</table>"
            return cftable
        if act == 'delete':
            # Delete connection
            flash('Connection Deleted!','important')
            # Delete file
            delfile = confPath+'conn'+os.path.sep+request.form['con']+'.yml'
            os.remove(delfile)
            return redirect("/connections")

    else:
        # List connections in folder ignoring .keep files
        confiles = do.listCfgFiles('conn')
        # Create a connections array
        connections = []
        # Iterate through each file
        for cfile in confiles:
            cfname = confPath+'conn'+os.path.sep+cfile
            # Open each file and load YAML dicts into connections array
            with open(cfname,'r') as file:
                connections.append(yaml.full_load(file))
        return render_template('pages/connections.html', connections=connections)


@app.route('/data', methods=['GET', 'POST'])
@login_required
def data():
    if request.method == 'POST':
        # Data page wants something
        act = request.form['action']
        cons = do.listCfgFiles('conn')
        cons = list(map(lambda x: x.replace('.yml',''),cons))
        if act == 'add':
            # Add data page
            return render_template('pages/data-add.html', cons=cons)
        if act == 'gitquotes':
            # Get a list of quotes available from selected connection
            con = request.form['con']
            # Return HTML for quote select box
            return do.gitCryptoQuotes(con)
        if act == 'gitpairs':
            # Get a list of pairs with the selected quote
            con = request.form['con']
            quote = request.form['quote']
            # Return HTML for pairs select box
            return do.gitCryptoPairs(con,quote)
        if act == 'fin':
            # Setup of data has finished create the data YAML
            con = request.form['conSel']
            quote = request.form['quoteSel']
            symb = request.form['symbSel']
            start = request.form['start']
            do.createCryptoData(con,quote,symb,start)
            return redirect("/data")
        if act == 'sample':
            # Setup of data has finished create the data YAML
            data = request.form['data']
            fromdate = request.form['fromdate']
            todate = request.form['todate']
            timeframe = request.form['timeframe']
            selection = request.form['selection']
            do.createSample(data,fromdate,todate,timeframe,selection)
            return redirect("/data")
        if act == 'delete':
            # Delete file
            delfile = confPath+'data'+os.path.sep+request.form['id']+'.yml'
            os.remove(delfile)
            return redirect("/data")
        if act == 'enable':
            status = request.form['status']
            id = request.form['id']
            #print('ID:'+id+'Status:'+status,file=sys.stderr)
            dCfgFile = do.readCfgFile('data',id+'.yml')
            if status == 'true':
                dCfgFile['enabled'] = True
            else:
                dCfgFile['enabled'] = False
            #print(dCfgFile,file=sys.stderr)
            dCfgFile = yaml.dump(dCfgFile)
            do.writeCfgFile('data',id,dCfgFile)
            return redirect("/data")
        if act == 'delete-sample':
            # Delete file
            delfile = dataPath+'samples'+os.path.sep+request.form['id']+'.feather'
            os.remove(delfile)
            return redirect("/data")
    else:
        # List data in folder ignoring .keep files
        dataCfgfiles = do.listCfgFiles('data')
        # Create data info array
        data = []
        # Iterate through each file
        for dfile in dataCfgfiles:
            tempData = do.readCfgFile('data',dfile)
            tempData['first'] = datetime.datetime.utcfromtimestamp(tempData['first']/1000).strftime('%Y-%m-%d')
            tempData['start'] = datetime.datetime.utcfromtimestamp(tempData['start']/1000).strftime('%Y-%m-%d')
            if tempData['end'] > 0:
                tempData['end'] = datetime.datetime.utcfromtimestamp(tempData['end']/1000).strftime('%Y-%m-%d')
            data.append(tempData)

        # List samples in folder ignoring .keep files
        samDatafiles = do.listDataFiles('samples')
        # Create data info array
        samples = []
        info = {}
        # Iterate through each file
        for dfile in samDatafiles:
            dstr = os.path.splitext(dfile)[0]
            parts = dstr.split('_')
            #print(parts,file=sys.stderr)
            info = {'id': dstr, 'con': parts[0], 'symb': parts[1]+'/'+parts[2], 'timeframe':parts[3], 'from':int(parts[4]), 'to':int(parts[5])}
            info['from'] = datetime.datetime.utcfromtimestamp(info['from']/1000).strftime('%Y-%m-%d')
            info['to'] = datetime.datetime.utcfromtimestamp(info['to']/1000).strftime('%Y-%m-%d')
            samples.append(info)
        return render_template('pages/data.html', data=data, samples=samples)


@app.route('/alchemy-enrich', methods=['GET', 'POST'])
@login_required
def alchemyenrich():
    if request.method == 'POST':
        # Data page wants something
        act = request.form['action']
        if act == 'add':
            # Add data page
            enlist = en.listIndi()
            return render_template('pages/alchemy-enrich-add.html', enlist=enlist)
        if act == 'fin':
            enname = request.form['enname']
            enriches = request.form['enriches']
            enstr = 'enname: '+enname+"\n"
            enrichlist = []
            for item in request.form.getlist('enriches'):
                enrichlist.append(item)
            enstr = enstr + 'riches: ' + ', '.join(enrichlist) + "\n"
            enstr = enstr + 'total: ' + str(len(enrichlist)) + "\n"
            do.writeCfgFile('enrich',enname,enstr)
            return redirect("/alchemy-enrich")
        if act == 'delete':
            # Delete file
            delfile = confPath+'enrich'+os.path.sep+request.form['enname']+'.yml'
            os.remove(delfile)
            return redirect("/alchemy-enrich")
    else:
        # List enrichments in folder ignoring .keep files
        enCfgFiles = do.listCfgFiles('enrich')
        # Create enrich info array
        enriches = []
        # Iterate through each file
        for enfile in enCfgFiles:
            endata = do.readCfgFile('enrich',enfile)
            enriches.append(endata)
        return render_template('pages/alchemy-enrich.html', enriches=enriches)

@app.route('/alchemy-nugs', methods=['GET', 'POST'])
@login_required
def alchemynugs():
    if request.method == 'POST':
        # Data page wants something
        act = request.form['action']
        if act == 'add':
            samplist = do.listDataFiles('samples')
            samples = do.samplesInfo(samplist)
            enrichlist = do.listCfgFiles('enrich')
            enrichments = [os.path.splitext(x)[0] for x in enrichlist]
            depens = en.listDepen();
            nanas = en.listNaN();
            return render_template('pages/alchemy-nugs-add.html', samples=samples, enrichments=enrichments, depens=depens, nanas=nanas)
        if act == 'fin':
            sample = request.form['sample']
            indie = request.form['indie']
            depen = request.form['depen']
            nana = request.form['nana']
            do.createNugget(sample,indie,depen,nana)
            return redirect("/alchemy-nugs")
        if act == 'delete':
            # Delete file
            delfile = dataPath+'nuggets'+os.path.sep+request.form['id']+'.feather'
            os.remove(delfile)
            return redirect("/alchemy-nugs")
    else:
        # List samples in folder ignoring .keep files
        nugfiles = do.listDataFiles('nuggets')
        # Pull nuggets info from above files
        nuggets = do.nuggetsInfo(nugfiles)
        return render_template('pages/alchemy-nugs.html', nuggets=nuggets)

@app.route('/observe', methods=['GET', 'POST'])
@login_required
def observe():
    if request.method == 'POST':
        # Observe page wants something
        act = request.form['action']
        nugget = request.form['nugget']
        if act == 'viewNug':
            script, div = ch.viewNugget(nugget)
        if act == 'viewCorr':
            script, div = ch.viewCorr(nugget)
        if act == 'viewFeat':
            script, div = ch.viewFeat(nugget)
        # List samples in folder ignoring .keep files
        nugfiles = do.listDataFiles('nuggets')
        # Pull nuggets info from above files
        nuggets = do.nuggetsInfo(nugfiles)
        return render_template('pages/observe.html', selected=nugget, nuggets=nuggets, script=script, div=div)
    else:
        # List samples in folder ignoring .keep files
        nugfiles = do.listDataFiles('nuggets')
        # Pull nuggets info from above files
        nuggets = do.nuggetsInfo(nugfiles)
        return render_template('pages/observe.html', nuggets=nuggets)

@app.route('/ai')
@login_required
def ai():
    return render_template('pages/ai.html')

@app.route('/sentiment')
@login_required
def sentiment():
    return render_template('pages/sentiment.html')

@app.route('/backtest')
@login_required
def backt():
    return render_template('pages/backtest.html')

@app.route('/trading')
@login_required
def trading():
    return render_template('pages/trading.html')

@app.route('/ops')
@login_required
def ops():
    return render_template('pages/ops.html')

@app.route('/changelogs')
@login_required
def changelogs():
    return render_template('pages/changelogs.html')

# User templates

@app.route('/login', methods=['GET', 'POST'])
def login():
    logform = LoginForm()
    #print(request.form,file=sys.stderr)
    name = request.form.get('name')
    #email = request.form.get('email')
    password = request.form.get('password')
    #remember = True if request.form.get('remember') else False
    if logform.validate_on_submit():
        #print("XXXXXX",file=sys.stderr)
        # Check for existence of username
        user = User.query.filter_by(name=name).first()
        # Check if user actually exists and then
        # take the user supplied password, hash it, and compare it to the hashed password in database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login')) # if user doesn't exist or password is wrong, reload the page
        login_user(user)
        return redirect(url_for('home'))
    return render_template('forms/login.html', form=logform)


@app.route("/logout")
def logout():
    # Clear flashes
    session.pop('_flashes', None)
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    print(request.form,file=sys.stderr)
    if form.validate_on_submit():
        # Get variables
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        # Check for existsing user and push back to register page if exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Please check your login details and try again.')
            return redirect(url_for('register'))
        # Create a new user object of User with the above data
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
        # Add this new user to the database
        db.session.add(new_user)
        db.session.commit()
        # Form finished successfully go to login
        return redirect('/login')
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

# Error handlers.

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#


# Default port:
if __name__ == '__main__':
    # Config App
    app.config.from_object(ConfigAPS())
    scheduler.init_app(app)
    scheduler.start()
    # Init debugger
    #toolbar = DebugToolbarExtension(app)
	# Overwrite config for flask-debugtoolbar
    #app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['DEBUG'] = True
    do.clearRunLocks()
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
