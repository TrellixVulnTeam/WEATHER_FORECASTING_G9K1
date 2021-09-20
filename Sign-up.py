from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pickle
import pandas as pd
import numpy as np
import json
import numpy as np
import urllib
from sklearn.metrics import mean_squared_error, r2_score
from math import sqrt
from statsmodels.tsa.vector_ar.var_model import VAR 
import datetime

app = Flask(__name__)
app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Achich123'
app.config['MYSQL_DB'] = 'pythonlogin'
mysql = MySQL(app)


@app.route('/pythonlogin/reg', methods=['POST',"GET"])
def reg():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:
                    msg = 'Account already exists!'
                    return render_template ("register.html", msg=msg)
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    msg = 'Invalid email address!'
                    return render_template ("register.html", msg=msg)
            elif not re.match(r'[A-Za-z0-9]+', username):
                    msg = 'Username must contain only characters and numbers!'
                    return render_template ("register.html", msg=msg)
            elif not username or not password or not email:
                    msg = 'Please fill out the form!'
                    return render_template ("register.html", msg=msg)
            else :
                    cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
                    mysql.connection.commit()
                    msg='You have successfully registered'
            return render_template('Sign-in.html', msg=msg)
    elif request.method == 'POST':
             msg = 'Please fill out the form!'
             return render_template ("register.html", msg=msg) 
          
@app.route('/pythonlogin/', methods = [ 'POST', 'GET'])
def form_login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                msg = username
                return redirect(url_for('home'))     
        else:
                msg='Maybe  username/password is incorrect'
    return render_template('Sign-in.html', msg=msg)  

@app.route('/home/')
def home():
    if 'loggedin' in session:
        def invert_transformation(df_train, df_forecast, second_diff=False):
                                df_fc = df_forecast.copy()
                                columns = df_train.columns
                                for col in columns:        
                                        # Roll back 2nd Diff
                                        if second_diff:
                                                df_fc[str(col)+'_1d'] = (df_train[col].iloc[-1]-df_train[col].iloc[-2]) + df_fc[str(col)+'_2d'].cumsum()
                                        # Roll back 1st Diff
                                        df_fc[str(col)+'_forecast'] = df_train[col].iloc[-1] + df_fc[str(col)+'_1d'].cumsum()
                                return df_fc
     ## retrieve the data from thingspeak
        df = urllib.request.urlopen(" https://api.thingspeak.com/channels/1419929/feeds.json?api_key=AQ6GZQVWX1LLHN79&results=5000")
        response = df.read()
        data = json.loads(response)
        df = pd.DataFrame(data["feeds"])
        df.columns = ["date", "entity","Temperature", "Humidite", "Pression"]
        df.index = pd.to_datetime(df['date']).dt.date
        df = df.drop(["date", 'entity'], axis =1)
        df = df.astype(float)
     ## Differentiate the data
        df_differenced = df.diff().dropna()
     ## Create the model
        model = VAR(df_differenced.values)
     ## Get the good order p
        for i in range(1, 100):
                previous = model.fit(i-1)
                result = model.fit(i)
                if result.aic > previous.aic:
                        p = i-1
                        break
                
     ## fit the model 
        model_fitted=model.fit(p)
     ## forecat the future value and de-differentiate it 
        lag_order = model_fitted.k_ar
        forecast_input = df_differenced.values[-lag_order:]
        fc = model_fitted.forecast(y=forecast_input, steps=1)
        time = [];
        for i in range(1):
                A = datetime.date.today() + datetime.timedelta(days=i)
                time.append(A)
        df_forecast = pd.DataFrame(fc, index=time, columns=df.columns + '_1d')
        df_results = invert_transformation(df, df_forecast, second_diff=False)
        df_results = df_results.loc[:, ["Temperature_forecast", "Humidite_forecast", "Pression_forecast"]]
     ## Create the variables which will contain the value for each parameter
        Temp = f'{round(df_results.Temperature_forecast[0], 4) }°C'
        hum = f'{round(df_results.Humidite_forecast[0], 4) }%'
        pres = f'{round(df_results.Pression_forecast[0], 4) }Kpa'
     ## Return values 
        return render_template('weather_forecasting.html', username=session['username'], Temp = Temp, hum = hum, pres = pres)
    return redirect(url_for('form_login'))

@app.route('/pythonlogin/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('form_login'))

@app.route('/about/')
def About():
   if 'loggedin' in session:
        return render_template('About.html', username=session['username'])
   return redirect(url_for('form_login'))

@app.route('/predict',methods=['POST', 'GET'])
def predict():
        if request.method == "POST":
                if "TD" in request.form:
                        def invert_transformation(df_train, df_forecast, second_diff=False):
                                df_fc = df_forecast.copy()
                                columns = df_train.columns
                                for col in columns:        
                                        # Roll back 2nd Diff
                                        if second_diff:
                                                df_fc[str(col)+'_1d'] = (df_train[col].iloc[-1]-df_train[col].iloc[-2]) + df_fc[str(col)+'_2d'].cumsum()
                                        # Roll back 1st Diff
                                        df_fc[str(col)+'_forecast'] = df_train[col].iloc[-1] + df_fc[str(col)+'_1d'].cumsum()
                                return df_fc
                        df = urllib.request.urlopen(" https://api.thingspeak.com/channels/1419929/feeds.json?api_key=AQ6GZQVWX1LLHN79&results=5000")
                        response = df.read()
                        data = json.loads(response)
                        df = pd.DataFrame(data["feeds"])
                        df.columns = ["date", "entity","Temperature", "Humidite", "Pression"]
                        df.index = pd.to_datetime(df['date']).dt.date
                        df = df.drop(["date", 'entity'], axis =1)
                        df = df.astype(float)
                        df_differenced = df.diff().dropna()
                        model = VAR(df_differenced.values)
                        for i in range(1, 100):
                                previous = model.fit(i-1)
                                result = model.fit(i)
                                if result.aic > previous.aic:
                                        p = i-1
                                        break
                        model_fitted=model.fit(p)
                        lag_order = model_fitted.k_ar
                        forecast_input = df_differenced.values[-lag_order:]
                        fc = model_fitted.forecast(y=forecast_input, steps=7)
                        time = [];
                        for i in range(7):
                                A = datetime.date.today() + datetime.timedelta(days=i)
                                time.append(A)
                        df_forecast = pd.DataFrame(fc, index=time, columns=df.columns + '_1d')
                        df_results = invert_transformation(df, df_forecast, second_diff=False)
                        df_results = df_results.loc[:, ["Temperature_forecast", "Humidite_forecast", "Pression_forecast"]]
                        df_results.to_csv('Weather_forecast_week.csv')  
                        path = "Weather_forecast_week.csv"
                        return send_file(path, as_attachment = True)
       
if __name__ == '__main__':
    app.debug = True
    app.run()
    