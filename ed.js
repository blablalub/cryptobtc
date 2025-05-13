async function createChart() {
  const response = await fetch('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1440');
  const data = await response.json();

  const labels = [];
  const prices = [];

  data.forEach(item => {
    const openTime = new Date(item[0]);
    const hours = openTime.getHours().toString().padStart(2, '0');
    const minutes = openTime.getMinutes().toString().padStart(2, '0');
    labels.push(`${hours}:${minutes}`);
    prices.push(parseFloat(item[4]));
  });

  const ctx = document.getElementById('myChart').getContext('2d');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Цена (USDT)',
        data: prices,
        borderColor: 'red',
        backgroundColor: 'rgba(255,0,0,0.2)',
        fill: true,
        pointRadius: 0,
        tension: 0.4,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: {
            color: '#444'
          },
          ticks: {
            color: '#fff'
          }
        },
        y: {
          grid: {
            color: '#444'
          },
          ticks: {
            color: '#fff'
          }
        }
      },
      plugins: {
        legend: {
          labels: {
            color: '#fff'
          }
        },
        tooltip: {
          backgroundColor: '#333',
          titleColor: '#fff',
          bodyColor: '#fff'
        }
      }
    }
  });
}
createChart();