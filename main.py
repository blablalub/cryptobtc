import requests
import pandas as pd
import json
import pytz  # импортируем для работы с часовыми поясами

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

df = fetch_bitcoin_data()

# Создаем объект часового пояса для Москвы
moscow_tz = pytz.timezone('Europe/Moscow')

# Переводим время в московский часовой пояс
df['Open Time'] = df['Open Time'].dt.tz_localize('UTC').dt.tz_convert(moscow_tz)

# Формируем метки времени в формате 'HH:MM' по московскому времени
labels = [dt.strftime('%H:%M') for dt in df['Open Time']]
prices = df['Close'].tolist()

# остальной код без изменений...
html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8" />
<title>Bitcoin Price Chart</title>
<!-- Подключение Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom"></script>
<style>
  #chartContainer {{
    width: 100%;
    max-width: 800px;
    height: auto;
    margin: auto;
  }}
  #myChart {{
    width: 100%;
    height: 100%;
  }}
</style>
</head>
<body>
<h2 style="text-align:center;">Bitcoin (BTC/USDT) Last 24 Hours</h2>
<div id="chartContainer">
    <canvas id="myChart"></canvas>
</div>
<script>
const ctx = document.getElementById('myChart').getContext('2d');
const chart = new Chart(ctx, {{
    type: 'line',
    data: {{
        labels: {json.dumps(labels)},
        datasets: [{{
            label: 'Цена BTC (USDT)',
            data: {json.dumps(prices)},
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1,
            pointRadius: 0,
            pointHoverRadius: 0
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
            legend: {{
                display: true
            }},
            tooltip: {{
                mode: 'index',
                intersect: false,
                callbacks: {{
                    label: function(context) {{
                        return 'Цена: ' + context.parsed.y.toFixed(2) + ' USDT';
                    }}
                }}
            }}
        }},
        interaction: {{
            mode: 'nearest',
            axis: 'x',
            intersect: false
        }},
        scales: {{
            x: {{
                display: true,
                title: {{
                    display: true,
                    text: 'Время'
                }},
                grid: {{
                    display: true,
                    drawBorder: true,
                    color: 'rgba(0,0,0,0.1)'
                }}
            }},
            y: {{
                beginAtZero: false,
                title: {{
                    display: true,
                    text: 'Цена (USDT)'
                }},
                grid: {{
                    display: true,
                    drawBorder: true,
                    color: 'rgba(0,0,0,0.1)'
                }}
            }}
        }}
    }}
}});
</script>
</body>
</html>
"""

with open('bitcoin_chart.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML файл создан: bitcoin_chart.html")