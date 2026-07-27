/// First, this formats the data from Excel to be used in the graph

        var DataFund = {{ arrayA }};
        var DataBenchmark = {{ arrayB }};

        var chartFund = [];  // initialize an empty array
        for(var i = 0; i < 0; i++) {
        chartFund.push([i, DataFund[i]]);  // add a pair [i, DataFund[i]] to the array
        }

        var chartBenchmark = [];  // initialize an empty array
        for(var i = 0; i < 0; i++) {
        chartBenchmark.push([i, DataBenchmark[i]]);  // add a pair [i, DataBenchmark[i]] to the array
        }
        var maxValue = {{ max_value }}; // Get maximum value for the player
        var minValue = - maxValue;

        // Format a payoff as currency with a space thousands separator, e.g. £1 000.00, -£20 000.00
        function formatPayoffCurrency(value) {
            var sign = value < 0 ? '-' : '';
            return sign + '£' + Highcharts.numberFormat(Math.abs(value), 2, '.', ' ');
        }

        var absMaxFund = Math.max(...DataFund.map(Math.abs)); // Get absolute maximum from DataFund
        var absMaxBenchmark = Math.max(...DataBenchmark.map(Math.abs)); // Get absolute maximum from DataBenchmark

        var dynamicMaxValue = Math.max(absMaxFund, absMaxBenchmark); // Choose the larger of the two
        var dynamicMinValue = -dynamicMaxValue; // Symmetric minimum value



var myChart; // Global variable to store the chart instance
var situations = ['Situation 1', 'Situation 2', 'Situation 3', 'Situation 4', 'Situation 5', 'Situation 6', 'Situation 7', 'Situation 8', 'Situation 9', 'Situation 10', 'Situation 11'];
var currentMonth = 0; // Initialize the current month index
var viewingAsset = 'A'; // Start by showing Asset A payoffs

// Update chart data function
function updateChartData() {
    // Clear existing series data
    myChart.series[0].setData([], true);
    myChart.series[1].setData([], true);

    if (viewingAsset === 'A') {
        // Display Asset A for the current month
        var ChartFund = [[currentMonth, DataFund[currentMonth]]];
        myChart.series[0].update({ showInLegend: true }, false); // Show Asset A in legend
        myChart.series[1].update({ showInLegend: false }, false); // Hide Asset B in legend
        myChart.series[0].setData(ChartFund, false); // Update Fund series
        myChart.series[1].setData([], false); // Clear Benchmark series
    } else if (viewingAsset === 'B') {
        // Display Asset B for the current month
        var ChartBenchmark = [[currentMonth, DataBenchmark[currentMonth]]];
        myChart.series[0].update({ showInLegend: false }, false); // Hide Asset A in legend
        myChart.series[1].update({ showInLegend: true }, false); // Show Asset B in legend
        myChart.series[0].setData([], false); // Clear Fund series
        myChart.series[1].setData(ChartBenchmark, false); // Update Benchmark series
    }

    // Update x-axis to display only the current year
    myChart.xAxis[0].update({
        min: currentMonth,
        max: currentMonth,
    });

    // Update the chart title with the current month
    myChart.setTitle({ text: situations[currentMonth] });
    currentMonth++; // Increment the month or switch to the next asset
    if (currentMonth >= DataFund.length || currentMonth >= situations.length) {
        if (viewingAsset === 'A') {
            // Finished all situations for Asset A, switch to Asset B
            viewingAsset = 'B';
            currentMonth = 0; // Restart month index for Asset B
        } else {
            // Finished all situations for both assets
            document.getElementById('updateChartButton').style.display = 'none'; // Hide the update button
            document.getElementById('b1').style.display = 'block'; // Show the Next button
            document.getElementById('b1').disabled = false; // Enable the Next button
        }
    }
}

/// Then, this creates the graph
function createChart() {
    myChart = Highcharts.chart('contr2', {
        chart: {
            backgroundColor: '#f8f9fa',
            type: 'column',
            width: 400,
            height: 400,
            marginLeft: 90,
            marginRight: 1,
            marginBottom: 60,
            marginf: 55,
<!--            events: {-->
<!--                load: function () {-->
<!--                    setTimeout(() => {-->
<!--                        animationComplete = true;-->
<!--                    }, animationtime/10);-->
<!--                }-->
<!--            }-->
        },
        title: {
             text: 'Month',
             align: 'left',
            x: 200
        },
        xAxis: {
            type: 'linear',
            labels: {
                enabled: false,
            },
            gridLineWidth: 1,
            pointPlacement: 'on',
            animation: false,
        },
        yAxis: {
            title: {
                style: {
                    fontSize: '20px'
                },
                text: 'Payoff'
            },
            labels: {
                style: {
                    fontSize: '14px'
                },
                enabled:true,
                formatter: function(){
                    // Add a pound symbol and thousands separator, and format the value to two decimal places
                    return formatPayoffCurrency(this.value);
                }
            },
            min: 0,
            max: maxValue,
            tickInterval: 0.5,
            plotLines: [{
                color: 'black',
                width: 1,
                value: 0,
                zIndex: 2
            }],
            lineWidth: 1,
            tickWidth: 1,
            tickLength: 5,
            opposite: false
        },
        plotOptions: {
            series: {
                borderColor: 'transparent',
                animation: false,
                lineWidth: 3,
                states: {
                    hover: {
                        lineWidth: 3,
                        marker: {
                            enabled: true
                        }
                    }
                },
                events: {
                    legendItemClick: function() {
                        return false;
                    }
                }
            },
            column: {
                pointPlacement: 'between',
                animation: false,
                events: {
                    legendItemClick: function () {
                        return false;
                    }
                },
                pointWidth: 50,
                dataLabels: {
                    style: {
                        fontSize: '8px'
                    },
                    enabled: false,
                    formatter: function() {
                        return this.y.toFixed(1)+'%';
                    }
                }
            }
        },
        credits: {
            enabled: false
        },
        tooltip: {
            formatter: function () {
                // Use the `situations` array to determine the month based on the x-axis value
                var month = situations[this.x % situations.length]; // Ensure it cycles through the situations
                return this.points.reduce(function (s, point) {
                    return s + '<br/>' + point.series.name + ': <b>' +
                        Highcharts.numberFormat(point.y, 2, '.', ' ') + '</b>';
                }, '<b>' + month + '</b>'); // Display the month in bold as the header
            },
            shared: true
        },

        legend: {
            align: 'center',
            enabled: true,
            squareSymbol: false,
            symbolHeight: 10,
            symbolWidth: 10,
            x: 45,
            y: 20, // Increase this value to move the legend down
            zIndex: 100,
            floating: true,
            backgroundColor: '#f8f9fa',
            shadow: false,
            itemStyle: {
                fontSize: '20px' // Increase the font size of the legend
            }
        },
        exporting: {
            enabled: false
        },
        series: [
        {
            name: 'Asset A',
            data: chartFund,
            color: '#00BFFF',
            pointPlacement: 'on',
            clip: false,
            zIndex: 1,
            id: 'main',
            pointPlacement: -0.04,
            pointRange: 1,
        },
        {
            name: 'Asset B',
            data: chartBenchmark,
            color: '#808080',
            pointPlacement: 'on',
            clip: false,
            zIndex: 0,
            pointPlacement: 0.04,
            pointRange: 1,
        },
        ]
    });
updateChartData();
}

// Initial call to create the chart with the first data point
createChart();

document.getElementById('updateChartButton').addEventListener('click', function() {
    updateChartData(); // Update chart data
});

// Set the interval to call incrementDataPoints every second
<!--var intervalId = setInterval(updateChartData, animationtime/10);-->