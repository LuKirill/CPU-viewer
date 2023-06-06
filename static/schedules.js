/* 
Получаем элемент canvas первого графика и контекст рисования
Создаем объект первого графика
Создаем функцию для обновления данных на первом графике
Обновляем первый график каждые 5 секунд

Получаем элемент canvas второго графика и контекст рисования
Создаем объект второго графика
Создаем функцию для обновления данных на первом графике
Обновляем первый график каждые 60 секунд
*/
var ctx = document.getElementById('cpu-chart').getContext('2d');
var cpuChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: [],
    datasets: [{
      label: 'График моментальной загрузки процессора в %',
      data: [],
      borderColor: 'crimson',
      borderWidth: 2,
      backgroundColor: 'crimson',
      fill: false
    }]
  },
  options: {
    responsive: false,
    title: {
      display: true,
      text: 'График моментальной загрузки процессора в %'
    },
    scales: {
      xAxes: [{
        type: 'time',
        distribution: 'series',
        ticks: {
          source: 'labels'
        }
      }],
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  }
});

function updateChart() {
  fetch('/momental-cpu-data')
    .then(response => response.json())
    .then(data => {
      cpuChart.data.labels = data.a;
      cpuChart.data.datasets[0].data = data.b;
      cpuChart.update();
    });
};
setInterval(updateChart, 5000);


var ctx = document.getElementById('average-chart').getContext('2d');
var cpuAverageChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: [],
    datasets: [{
      label: 'График усредненной загрузки процессора с ценой деления 1 минута в %',
      data: [],
      borderColor: 'crimson',
      borderWidth: 2,
      backgroundColor: 'crimson',
      fill: false
    }]
  },
  options: {
    responsive: false,
    title: {
      display: true,
      text: 'График усредненной загрузки процессора с ценой деления 1 минута в %'
    },
    scales: {
      xAxes: [{
        type: 'time',
        distribution: 'series',
        ticks: {
          source: 'labels'
        }
      }],
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  }
});

function updateAverageChart() {
  fetch('/average-cpu-data')
    .then(response => response.json())
    .then(data => {
      cpuAverageChart.data.labels = data.c;
      cpuAverageChart.data.datasets[0].data = data.d;
      cpuAverageChart.update();
    });
};
setInterval(updateAverageChart, 60000);