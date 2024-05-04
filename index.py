import os
import logging
import time
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from pandas_datareader import data as pdr
import random
import math
from flask import Flask, request, render_template, redirect, url_for
from statistics import mean, stdev
import json
import http.client
import requests
from concurrent.futures import ThreadPoolExecutor

# Configure Flask app
app = Flask(__name__)

# Set environment variables for AWS credentials file
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = './cred'

# Set up yfinance override
yf.pdr_override()

# Get stock data from Yahoo Finance
today = date.today()
decade_ago = today - timedelta(days=1095)
# Get stock data from Yahoo Finance for NVDA
data = pdr.get_data_yahoo('NVDA', start=decade_ago, end=today)

# Add Buy and Sell columns to the data
data['Buy'] = 0
data['Sell'] = 0

# Define function to find buy and sell signals
def find_signals(data):
    for i in range(2, len(data)):
        body = 0.01

        # Three Soldiers
        if (data.Close[i] - data.Open[i]) >= body \
                and data.Close[i] > data.Close[i - 1] \
                and (data.Close[i - 1] - data.Open[i - 1]) >= body \
                and data.Close[i - 1] > data.Close[i - 2] \
                and (data.Close[i - 2] - data.Open[i - 2]) >= body:
            data.at[data.index[i], 'Buy'] = 1

        # Three Crows
        if (data.Open[i] - data.Close[i]) >= body \
                and data.Close[i] < data.Close[i - 1] \
                and (data.Open[i - 1] - data.Close[i - 1]) >= body \
                and data.Close[i - 1] < data.Close[i - 2] \
                and (data.Open[i - 2] - data.Close[i - 2]) >= body:
            data.at[data.index[i], 'Sell'] = 1

# Call function to find signals
find_signals(data)

# Convert data to dictionary
data = data.reset_index()
data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
dict_data = data.to_dict(orient='list')

# Render template function
def do_render(tname, values={}):
    if not os.path.isfile(os.path.join(os.getcwd(), 'templates/' + tname)):
        return render_template('index.htm')
    return render_template(tname, **values)

# Define handler for /calculate route
@app.route('/calculate', methods=['POST'])
def init_handler():
    if request.method == 'POST':
        s = request.form.get('s')
        r = request.form.get('r')

        if s == 'lambda':
            conn = http.client.HTTPSConnection("hs02ojgqx9.execute-api.us-east-1.amazonaws.com")
            return do_render('form.htm', {'note': "Connected to " + str(conn)})
        elif s == 'ec2':
            # Implement warming up EC2 instances
            pass

# Define handler for /results route
@app.route('/results', methods=['POST'])
def calculate_handler():
    if request.method == 'POST':
        # Process request and generate results
        pass

# Define handler for /audit route
@app.route('/audit')
def audit_handler():
    # Retrieve audit data
    pass

# Define handler for /terminate route
@app.route('/terminate')
def terminate_handler():
    # Terminate EC2 instances
    pass

# Define main route handler
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def main_page(path):
    return do_render(path)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

