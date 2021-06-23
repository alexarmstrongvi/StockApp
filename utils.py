import json
import re
from datetime import datetime
import calendar
import sys

import requests
from dateutil import parser
import pandas as pd
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
from flask import flash, current_app

def get_stock_price_plotly_json(ticker, plot_type, month=None, year=None):
    fig = make_stock_price_plot(ticker, plot_type, month, year)
    if fig is None:
        return
    return json.dumps(fig, cls=PlotlyJSONEncoder)

def make_stock_price_plot(ticker, plot_type, month=None, year=None):
    df = get_stock_time_series(ticker, month, year)
    if df is None:
        return
    
    # Plotly
    if plot_type == 'adj_close':
        data = go.Scatter(x=df.index, y=df['adjusted close'], mode='lines+markers')
        fig = go.Figure(data)
        ylabel = "Adjusted Close Price ($)"
    else:
        fig = go.Figure(data=go.Candlestick(
            x=df.index,
            open  = df['open'],
            high  = df['high'],
            low   = df['low'],
            close = df['close']
        ))
        ylabel = 'Price ($)'
    
    fig.update_layout(
        title_text  = f'{ticker} Stock Price in {calendar.month_name[month]} {year}',
        xaxis_title = "Date",
        yaxis_title = ylabel,
        template='plotly_white'
    )
    return fig

def get_stock_time_series(ticker, month=None, year=None):
    if datetime.today() < datetime(year=year, month=month, day=1):
        flash("Sorry but this service is currently unable to predict the future")
        return

    data_raw = get_stock_ts_raw(ticker)
    if not data_raw:
        flash(f'Stock price data not found for {ticker}')
        return

    _, df = parse_stock_ts_raw(data_raw) 
    df_trim  = filter_stock_ts_df(df, month, year)

    if df_trim.empty:
        min_dt, max_dt = df.index.min(), df.index.max()
        mn = calendar.month_name    
        flash(f'Stock price data not available for {ticker} in {mn[month]} {year}.')
        flash(f'Data for {ticker} exists from {mn[min_dt.month]} {min_dt.year} to {mn[max_dt.month]} {max_dt.year}')
        return

    return df_trim

def get_stock_ts_raw(ticker):
    # TODO: add as args
    function   = 'TIME_SERIES_DAILY_ADJUSTED'
    outputsize = 'full'
    
    url = f'''
    https://www.alphavantage.co/query?
      function   = {function}
    & symbol     = {ticker}
    & outputsize = {outputsize}
    & apikey     = {current_app.config["ALPHA_VANTAGE_API_KEY"]}
    '''.replace(' ','').replace('\n','')
    
    r = requests.get(url)
    try:
        data = r.json()
    except json.JSONDecodeError:
        print("ERROR :: Failed to decode API data. Response status code =", r.status_code, file=sys.stderr)
        return 
    
    if 'Error Message' in data:
        print(data['Error Message'], file=sys.stderr)
        return
    
    return data

def parse_stock_ts_raw(data):
    meta = data['Meta Data']
    ts_key = [k for k in data if 'Time Series' in k][0]
    ts_df = pd.DataFrame(data[ts_key]).T

    # Clean up keys
    patt = re.compile(r'[0-9]*\.\ *') # Ex. match '11. ' in '11. Text'
    meta = {patt.sub('',k).strip():v for k,v in meta.items()}
    ts_df.columns = [patt.sub('',c).strip() for c in ts_df.columns]
    
    # Set datatype
    ts_df.index = pd.to_datetime(ts_df.index)
    ts_df = ts_df.astype({
        'open'              : 'float',
        'high'              : 'float',
        'low'               : 'float',
        'close'             : 'float',
        'adjusted close'    : 'float',
        'volume'            : 'int',
        'dividend amount'   : 'float',
        'split coefficient' : 'float'
    })
    
    return meta, ts_df

def filter_stock_ts_df(df, month=None, year=None):    
    if df.empty:
        return df

    # Convert month to start and end dates
    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month
    dt = parser.parse(f'{month:0>2}/01/{year}')
    if dt > datetime.now():
        dt.replace(year=datetime.now().year-1)
    
    # Get filter
    start = get_start_of_month(dt)
    end   = get_end_of_month(dt)
    filt  = df.index.to_series().between(start, end)

    return df[filt] 

def get_start_of_month(dt):
    return dt.replace(day=1)

def get_end_of_month(dt):
    return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])