from flask import Flask, render_template_string
import requests
import pandas as pd
import json
import pytz

app = Flask(__name__)

def fetch_bitcoin_data():
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': 'BTCUSDT',
        'interval': '1m',
        'limit': 1440
    }
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close Time', 'Quote Asset Volume', 'Number of Trades',
        'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'
    ])
    df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
    df['Close'] = df['Close'].astype(float)
    return df[['Open Time', 'Close']]

@app.route('/')
def index():
    df = fetch_bitcoin_data()

    # Переводим время в московский часовой пояс
    moscow_tz = pytz.timezone('Europe/Moscow')
    df['Open Time'] = df['Open Time'].dt.tz_localize('UTC').dt.tz_convert(moscow_tz)

    # Формируем метки времени
    labels = [dt.strftime('%H:%M') for dt in df['Open Time']]
    prices = df['Close'].tolist()

    # HTML-шаблон с Chart.js
    html_template = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
    <meta charset="UTF-8" />
    <title>Bitcoin Price Chart</title>
    <!-- Подключение Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom"></script>
    <style>
      #chartContainer {
        width: 100%;
        max-width: 800px;
        height: auto;
        margin: auto;
      }
      #myChart {
        width: 100%;
        height: 100%;
      }
    </style>
    </head>
    <body>
    <h2 style="text-align:center;">Bitcoin (BTC/USDT) Last 24 Hours</h2>
    <div id="chartContainer">
        <canvas id="myChart"></canvas>
    </div>
    <script>
    const ctx = document.getElementById('myChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: {{ labels|safe }},
            datasets: [{
                label: 'Цена BTC (USDT)',
                data: {{ prices|safe }},
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1,
                pointRadius: 0,
                pointHoverRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return 'Цена: ' + context.parsed.y.toFixed(2) + ' USDT';
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Время'
                    },
                    grid: {
                        display: true,
                        drawBorder: true,
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Цена (USDT)'
                    },
                    grid: {
                        display: true,
                        drawBorder: true,
                        color: 'rgba(0,0,0,0.1)'
                    }
                }
            }
        }
    });
    </script>
    </body>
    </html>
    """

    # Передача данных в шаблон
    return render_template_string(html_template, labels=json.dumps(labels), prices=json.dumps(prices))

if __name__ == '__main__':
    app.run(debug=True)