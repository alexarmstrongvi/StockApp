from flask import Flask, render_template, request, redirect
from flask.helpers import flash, make_response, send_file, url_for
from flask.wrappers import Response

import base64
from datetime import date

import utils

app = Flask(__name__)

app.config.from_mapping(SECRET_KEY='dev')

@app.route('/')
def index():
  m = date.today().month
  y = date.today().year
  return render_template('index.html', current_month=m, current_year=y)

@app.route('/about')
def about():
  return render_template('about.html')
import sys

@app.route('/get_ticker', methods=['GET', 'POST'])
def get_ticker():
  if request.method == 'POST':
    # Parse request form
    ticker    = request.form['ticker']
    plot_type = request.form['plot_type']
    month     = int(request.form['month'])
    try:
      year = int(request.form['year'])
    except ValueError: # year field left empty
      flash("Please provide a year")
      return redirect(url_for('index'))
    

    # Generate plot
    print(f"Form Inputs : {ticker=}; {month=}; {year=}", file=sys.stderr)
    graphJSON = utils.get_stock_price_plotly_json(ticker, plot_type, month, year)
    return str(render_template('stock_price_plotly.html', graphJSON=graphJSON))
  else:
    return redirect(url_for('index'))

if __name__ == '__main__':
  app.run(port=33507)
