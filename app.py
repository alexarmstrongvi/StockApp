from datetime import date

from dotenv import load_dotenv; load_dotenv()
from flask import Flask, flash, url_for, render_template, request, redirect

import utils

################################################################################
# Configure Flask Application
################################################################################
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('default_settings')
app.config.from_pyfile('config.py', silent=True)

################################################################################
# Views
################################################################################
@app.route('/')
def index():
  return render_template('index.html', 
    current_month = date.today().month, 
    current_year  = date.today().year
  )

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
    graphJSON = utils.get_stock_price_plotly_json(ticker, plot_type, month, year)
    
    # Return webpage
    return render_template('stock_price_plotly.html', graphJSON=graphJSON)

  # Only accessible through home page form submission
  return redirect(url_for('index'))

################################################################################
if __name__ == '__main__':
  app.run(port=33507)
