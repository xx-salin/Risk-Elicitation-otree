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

        var absMaxFund = Math.max(...DataFund.map(Math.abs)); // Get absolute maximum from DataFund
        var absMaxBenchmark = Math.max(...DataBenchmark.map(Math.abs)); // Get absolute maximum from DataBenchmark

        var dynamicMaxValue = Math.max(absMaxFund, absMaxBenchmark); // Choose the larger of the two
        var dynamicMinValue = -dynamicMaxValue; // Symmetric minimum value

        // Round a rough step up to a "nice" 1/2/2.5/5/10 (times a power of ten)
        // value, e.g. niceStep(0.44) -> 0.5, niceStep(430) -> 500.
        function niceStep(roughStep) {
            if (!roughStep || roughStep <= 0) return 1;
            var exponent = Math.floor(Math.log10(roughStep));
            var fraction = roughStep / Math.pow(10, exponent);
            var niceFraction;
            if (fraction <= 1) niceFraction = 1;
            else if (fraction <= 2) niceFraction = 2;
            else if (fraction <= 2.5) niceFraction = 2.5;
            else if (fraction <= 5) niceFraction = 5;
            else niceFraction = 10;
            return niceFraction * Math.pow(10, exponent);
        }

        var yTickInterval, yMax;
        if (axisScale === 'rlocal') {
            // axis_scale: "rlocal" rescales the y-axis each round to that round's own min/max payoffs
            yTickInterval = niceStep(dynamicMaxValue / 5);
            yMax = yTickInterval * Math.ceil((dynamicMaxValue || 1) / yTickInterval);
        } else {
            // "global" (default)
            var BASE_MAX_VALUE = 2.2;
            var NICE_BASE_STEP = 0.5;
            var TICKS_ABOVE_ZERO = Math.ceil(BASE_MAX_VALUE / NICE_BASE_STEP);
            yTickInterval = maxValue > 0 ? NICE_BASE_STEP * (maxValue / BASE_MAX_VALUE) : 1;
            yMax = yTickInterval * TICKS_ABOVE_ZERO;
        }

        // colorTreatment (set in Payoffs_Together.html): 0 = color-code bars
        // red/green for loss/gain, 1 = keep the series' own neutral color.
        // In the color-coded treatment, both assets are red (loss) / green (gain),
        // so Asset A stays a solid fill and Asset B is additionally given a
        // diagonal-line pattern (in the same red/green) to tell the assets apart.
        function linePattern(color) {
            return {
                pattern: {
                    path: {
                        d: 'M 0 10 L 10 0 M -1 1 L 1 -1 M 9 11 L 11 9',
                        stroke: color,
                        strokeWidth: 2
                    },
                    width: 10,
                    height: 10
                }
            };
        }

        var lossGainZonesA = colorTreatment === 0
            ? [{ value: 0, color: '#dc2626' }, { color: '#16a34a' }]
            : undefined;
        var lossGainZonesB = colorTreatment === 0
            ? [{ value: 0, color: linePattern('#dc2626') }, { color: linePattern('#16a34a') }]
            : undefined;

        // Base series color: used directly as the actual bar fill in the neutral
        // (non-color-coded) treatment, since no zones are defined there, and as
        // the legend swatch in the color-coded treatment (where zones take over
        // the actual bars). Both assets share the same grey; Asset A stays solid
        // and Asset B gets the line pattern, so the fill-vs-pattern distinction
        // (not color) is what tells them apart in both treatments alike.
        var assetAColor = '#808080';
        var assetBColor = linePattern('#808080');

        // Always outline both assets' bars in black (regardless of color treatment),
        // so a zero-payoff bar (no height/fill) is still visible.
        var assetABorderColor = '#000000';
        var assetBBorderColor = '#000000';
        var assetBorderWidth = 3;

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
            animation: false,
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
            // The x-axis's own line would otherwise sit at the bottom of the
            // plot area (yAxis.min); hidden here since the black axis line
            // should instead sit at the £0.00 tick - see yAxis.plotLines below.
            lineWidth: 0,
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
            // Stands in for the x-axis (hidden above) - a solid black line at the
            // £0.00 tick, so the "axis" reads at zero rather than at the bottom.
            plotLines: [{
                color: '#000000',
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
                pointWidth: 30, // matches the simultaneous-group chart, so bar width/spacing looks the same across both
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
            shared: true,
            // Pin the tooltip to the top-left corner so it never covers either bar.
            positioner: function () {
                return { x: 40, y: 40 };
            },
            animation: false
        },

        legend: {
            align: 'center',
            enabled: true,
            squareSymbol: true,
            symbolHeight: 14,
            symbolWidth: 22,
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
            color: assetAColor,
            zones: lossGainZonesA,
            zoneAxis: 'y',
            borderColor: assetABorderColor,
            borderWidth: assetBorderWidth,
            pointPlacement: 'on',
            clip: false,
            zIndex: 1,
            id: 'main',
            pointPlacement: 0.06,
            pointRange: 1,
        },
        {
            name: 'Asset B',
            data: chartBenchmark,
            color: assetBColor,
            zones: lossGainZonesB,
            zoneAxis: 'y',
            borderColor: assetBBorderColor,
            borderWidth: assetBorderWidth,
            pointPlacement: 'on',
            clip: false,
            zIndex: 0,
            pointPlacement: -0.06,
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

