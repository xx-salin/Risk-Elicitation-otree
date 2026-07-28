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

        // Round a value up to N significant figures, e.g. roundUpToSigFigs(18.5, 2) -> 19.
        function roundUpToSigFigs(value, sigFigs) {
            if (!value) return 0;
            var magnitude = Math.pow(10, sigFigs - Math.ceil(Math.log10(Math.abs(value))));
            return Math.ceil(value * magnitude) / magnitude;
        }

        // Always show 5 evenly spaced, 2-sig-fig tick marks above zero,
        // regardless of the stakes multiplier (F*X) baked into maxValue.
        var yTickInterval = maxValue > 0 ? roundUpToSigFigs(maxValue / 5, 2) : 1;
        var yMax = yTickInterval * 5;

        var absMaxFund = Math.max(...DataFund.map(Math.abs)); // Get absolute maximum from DataFund
        var absMaxBenchmark = Math.max(...DataBenchmark.map(Math.abs)); // Get absolute maximum from DataBenchmark

        var dynamicMaxValue = Math.max(absMaxFund, absMaxBenchmark); // Choose the larger of the two
        var dynamicMinValue = -dynamicMaxValue; // Symmetric minimum value

        // colorTreatment (set in Payoffs_Together.html): 0 = color-code bars
        // red/green for loss/gain, 1 = keep the series' own neutral color.
        var lossGainZones = colorTreatment === 0
            ? [{ value: 0, color: '#dc2626' }, { color: '#16a34a' }]
            : undefined;

        // When bars are loss/gain colored, the fill no longer identifies the
        // asset, so add a thick per-asset outline instead (A = blue, B = black).
        var assetABorderColor = colorTreatment === 0 ? '#00BFFF' : 'transparent';
        var assetBBorderColor = colorTreatment === 0 ? '#000000' : 'transparent';
        var assetBorderWidth = colorTreatment === 0 ? 3 : 0;

var myChart; // Global variable to store the chart instance
var situations = DataFund.map((_, i) => 'Situation ' + (i + 1)); // one label per actual situation, however many there are
var currentMonth = 0; // Initialize the current month index

// Update chart data function
function updateChartData() {
    // Clear existing series data
    myChart.series[0].setData([], true);
    myChart.series[1].setData([], true);

    // Add data points for the current year
    var ChartFund = [[currentMonth, DataFund[currentMonth]]];
    var ChartBenchmark = [[currentMonth, DataBenchmark[currentMonth]]];

    // Update the chart with the current data point
    myChart.series[0].setData(ChartFund, false); // Update Fund series
    myChart.series[1].setData(ChartBenchmark, false); // Update Benchmark series

    // Update x-axis to display only the current year
    myChart.xAxis[0].update({
        min: currentMonth,
        max: currentMonth,
    });

    // Update the chart title with the current month
    myChart.setTitle({ text: situations[currentMonth] });
    currentMonth++; // Increment the current month index

    if (currentMonth >= DataFund.length || currentMonth >= situations.length) {
        document.getElementById('updateChartButton').style.display = 'none'; // Hide the update button
        document.getElementById('b1').style.display = 'block'; // Show the Next button
        document.getElementById('b1').disabled = false; // Enable the Next button
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
            x: 200,
            style: {
                color: '#000000'
            }
        },
        xAxis: {
            type: 'linear',
            labels: {
                enabled: false,
            },
            gridLineWidth: 0,
            lineColor: '#000000',
            pointPlacement: 'on',
            animation: false,
        },
        yAxis: {
            title: {
                style: {
                    fontSize: '20px',
                    color: '#000000'
                },
                text: 'Payoff'
            },
            labels: {
                style: {
                    fontSize: '14px',
                    color: '#000000'
                },
                enabled:true,
                formatter: function(){
                    // Add a pound symbol and thousands separator, and format the value to two decimal places
                    return formatPayoffCurrency(this.value);
                }
            },
            min: -yMax,
            max: yMax,
            tickInterval: yTickInterval,
            plotLines: [{
                color: 'lightgrey',
                width: 1,
                value: 0,
                zIndex: 2
            }],
            gridLineColor: 'lightgrey',
            lineColor: '#000000',
            lineWidth: 1,
            tickWidth: 1,
            tickColor: 'lightgrey',
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
                fontSize: '20px', // Increase the font size of the legend
                color: '#000000'
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
            zones: lossGainZones,
            zoneAxis: 'y',
            borderColor: assetABorderColor,
            borderWidth: assetBorderWidth,
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
            zones: lossGainZones,
            zoneAxis: 'y',
            borderColor: assetBBorderColor,
            borderWidth: assetBorderWidth,
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

