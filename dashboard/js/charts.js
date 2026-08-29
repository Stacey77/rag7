// Chart.js Configurations
class ChartManager {
    constructor() {
        this.charts = {};
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#B8B8B8',
                        font: {
                            family: 'Inter, sans-serif'
                        }
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        color: '#B8B8B8'
                    },
                    grid: {
                        color: 'rgba(123, 104, 166, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#B8B8B8'
                    },
                    grid: {
                        color: 'rgba(123, 104, 166, 0.1)'
                    }
                }
            }
        };
    }

    initializeCharts(metricsData) {
        this.createBlastRadiusChart();
        this.createBandwidthChart(metricsData.bandwidth);
        this.createComputeChart(metricsData.compute);
        this.createStorageChart(metricsData.storage);
        this.createCostTrendChart(metricsData.costTrend);
    }

    createBlastRadiusChart() {
        const ctx = document.getElementById('blastRadiusChart');
        if (!ctx) return;

        this.charts.blastRadius = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Compute', 'Storage', 'Network', 'Security'],
                datasets: [{
                    data: [12, 5, 4, 3],
                    backgroundColor: [
                        'rgba(91, 75, 138, 0.8)',
                        'rgba(123, 104, 166, 0.8)',
                        'rgba(255, 107, 53, 0.8)',
                        'rgba(76, 175, 80, 0.8)'
                    ],
                    borderColor: [
                        'rgb(91, 75, 138)',
                        'rgb(123, 104, 166)',
                        'rgb(255, 107, 53)',
                        'rgb(76, 175, 80)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#B8B8B8',
                            padding: 15,
                            font: {
                                family: 'Inter, sans-serif',
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(46, 37, 71, 0.95)',
                        titleColor: '#FFFFFF',
                        bodyColor: '#B8B8B8',
                        borderColor: 'rgba(123, 104, 166, 0.5)',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: true
                    }
                }
            }
        });
    }

    createBandwidthChart(data) {
        const ctx = document.getElementById('bandwidthChart');
        if (!ctx) return;

        this.charts.bandwidth = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Bandwidth Savings (GB)',
                    data: data.data,
                    borderColor: 'rgb(76, 175, 80)',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: 'rgb(76, 175, 80)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(46, 37, 71, 0.95)',
                        titleColor: '#FFFFFF',
                        bodyColor: '#B8B8B8',
                        borderColor: 'rgba(76, 175, 80, 0.5)',
                        borderWidth: 1
                    }
                }
            }
        });
    }

    createComputeChart(data) {
        const ctx = document.getElementById('computeChart');
        if (!ctx) return;

        this.charts.compute = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Utilization (%)',
                    data: data.data,
                    backgroundColor: 'rgba(91, 75, 138, 0.8)',
                    borderColor: 'rgb(91, 75, 138)',
                    borderWidth: 2,
                    borderRadius: 6
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(46, 37, 71, 0.95)',
                        titleColor: '#FFFFFF',
                        bodyColor: '#B8B8B8'
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        max: 100,
                        ticks: {
                            color: '#B8B8B8',
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    createStorageChart(data) {
        const ctx = document.getElementById('storageChart');
        if (!ctx) return;

        this.charts.storage = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Used', 'Free'],
                datasets: [{
                    data: [data.used, data.free],
                    backgroundColor: [
                        'rgba(255, 107, 53, 0.8)',
                        'rgba(123, 104, 166, 0.3)'
                    ],
                    borderColor: [
                        'rgb(255, 107, 53)',
                        'rgb(123, 104, 166)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#B8B8B8',
                            font: {
                                family: 'Inter, sans-serif',
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(46, 37, 71, 0.95)',
                        titleColor: '#FFFFFF',
                        bodyColor: '#B8B8B8',
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    createCostTrendChart(data) {
        const ctx = document.getElementById('costTrendChart');
        if (!ctx) return;

        this.charts.costTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Cost ($)',
                    data: data.data,
                    borderColor: 'rgb(255, 107, 53)',
                    backgroundColor: 'rgba(255, 107, 53, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: 'rgb(255, 107, 53)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(46, 37, 71, 0.95)',
                        titleColor: '#FFFFFF',
                        bodyColor: '#B8B8B8',
                        callbacks: {
                            label: function(context) {
                                return '$' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        ticks: {
                            color: '#B8B8B8',
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    }
                }
            }
        });
    }

    updateChart(chartName, newData) {
        const chart = this.charts[chartName];
        if (!chart) return;

        if (newData.labels) {
            chart.data.labels = newData.labels;
        }
        if (newData.datasets) {
            chart.data.datasets = newData.datasets;
        }
        
        chart.update();
    }

    destroyChart(chartName) {
        const chart = this.charts[chartName];
        if (chart) {
            chart.destroy();
            delete this.charts[chartName];
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(chartName => {
            this.destroyChart(chartName);
        });
    }
}

// Export chart manager instance
const chartManager = new ChartManager();
