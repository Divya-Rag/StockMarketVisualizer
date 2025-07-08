from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objs as go

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    chart_html = None
    stock_symbol = ''
    chart_type = 'line'  # default chart type

    if request.method == 'POST':
        stock_symbol = request.form['symbol'].upper()
        chart_type = request.form.get('chart_type', 'line')

        # Set date range
        end = datetime.datetime.today()
        start = end - datetime.timedelta(days=30)

        try:
            # Download stock data
            data = yf.download(stock_symbol, start=start, end=end, interval='1d', threads=False)

            # Flatten MultiIndex columns if necessary
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0] for col in data.columns]

            data = data.dropna()

            # Calculate 7-day moving average
            data['7MA'] = data['Close'].rolling(window=7).mean()

            fig = go.Figure()

            if chart_type == 'line':
                # Line chart for close price
                fig.add_trace(go.Scatter(
                    x=data.index, y=data['Close'],
                    mode='lines+markers',
                    name='Close Price',
                    line=dict(color='blue')
                ))

                # Add 7-day moving average
                fig.add_trace(go.Scatter(
                    x=data.index, y=data['7MA'],
                    mode='lines',
                    name='7-Day Moving Avg',
                    line=dict(color='orange', dash='dot')
                ))

            elif chart_type == 'candlestick':
                fig.add_trace(go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='Candlestick'
                ))

            # Volume bar chart
            fig.add_trace(go.Bar(
                x=data.index, y=data['Volume'],
                name='Volume',
                yaxis='y2',
                marker_color='lightgray',
                opacity=0.4
            ))
            fig.update_layout(
               title={
                   'text': f"{stock_symbol.upper()} Stock - Last 30 Days",
                   'x': 0.5,
                   'xanchor': 'center',
                   'y': 0.95  # Slightly lower so it's not touching the top
                },
                margin=dict(t=120),  # More space at the top
                xaxis_title='Date',
                yaxis=dict(title='Price in USD'),
                yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False),
                legend=dict(
                    x=0.5,
                    y=1.10,  # Move legend lower than title
                    xanchor="center",
                    orientation="h"
                ),
                height=600,
                plot_bgcolor="#f8f8f8"
            )



            chart_html = fig.to_html(full_html=False)

        except Exception as e:
            chart_html = f"<p style='color:red;'>Error: {e}</p>"

    return render_template('index.html', chart=chart_html, symbol=stock_symbol, selected_type=chart_type)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)

