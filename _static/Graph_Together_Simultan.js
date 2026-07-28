/// First, this formats the data from Excel to be used in the graph
        var DataFund = {{ arrayA }};  // Convert proportions to percentages for Fund data
        var DataBenchmark = {{ arrayB }};  // Convert proportions to percentages for Benchmark data

        var numStates = DataFund.length;
        var fundLabels = [];
        var chartFund = DataFund
            .map((val, i) => ({ val, i }))
            .sort((a, b) => a.val - b.val)
            .map((obj, sortedIdx) => {
                fundLabels[sortedIdx] = obj.i + 1;
                return { x: sortedIdx, y: obj.val, label: obj.i + 1 };
            });

        var benchmarkLabels = [];
        var chartBenchmark = DataBenchmark
            .map((val, i) => ({ val, i }))
            .sort((a, b) => a.val - b.val)
            .map((obj, sortedIdx) => {
                benchmarkLabels[sortedIdx] = obj.i + 1;
                return { x: sortedIdx, y: obj.val, label: obj.i + 1 };
            });

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

        // Always outline both assets' bars in black (regardless of color treatment),
        // so a zero-payoff bar (no height/fill) is still visible.
        var assetABorderColor = '#000000';
        var assetBBorderColor = '#000000';
        var assetBorderWidth = 3;

/// Then, this creates the graph
$(function () {
    Highcharts.chart('contr2', {
        chart: {
            backgroundColor: '#f8f9fa',
            type: 'column',
            height: 400,
            marginRight: 30,
            marginBottom: 100,
            marginf: 55,
            animation: false,
            events: {
                load: function () {
                    setTimeout(() => {
                        animationComplete = true;
                    }, animationtime/10);
                }
            }
        },
        title: {
            text: ''
        },
        xAxis: {
            type: 'linear',
            tickWidth: 0,
            lineColor: '#000000',
            labels: {
                style: {
                    fontSize: '14px'
                },
                enabled: false,
                formatter: function() {
                    var f = fundLabels[this.value] !== undefined ? fundLabels[this.value] : this.value + 1;
                    var b = benchmarkLabels[this.value] !== undefined ? benchmarkLabels[this.value] : this.value + 1;
                    return f + '<br>' + b;
                },
            },
            gridLineWidth: 1,
            gridLineColor: 'lightgrey',
            tickInterval: 1,
            minTickInterval: 1, // Minimum interval of 1 between ticks
            min: 0,
            max: numStates - 1,
            endOnTick: false, // Prevent extending the axis to make it end on a tick
            startOnTick: false, // Start axis on a tick
            pointPlacement: 'on',
        },
        yAxis: {
            title: {
                style: {
                    fontSize: '15px',
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
                },
                point: {
                    events: {
                        mouseOver: function() {
                            let tmpX = this.x;

                            if (inX != tmpX && outX != tmpX) {
                                // Check if the mouse is over the same year as the last time
                                inX = tmpX;

                                if (startTime > 0) {
                                    // Timer was started before
                                    let tmpTime = new Date().getTime();

                                    let tmpTimeSpent = tmpTime - startTime;
                                    timeSpent.push([outX + 1, tmpTimeSpent]);
                                    startTime = tmpTime;

                                    document.getElementById('timeToNewTooltip').value = timeSpent; // Update the hidden field with the time spent
                                } else {
                                    startTime = new Date().getTime(); // First tooltip is loaded
                                }
                            }
                        },
                        mouseOut: function () {
                            outX = this.x;
                        }
                    }
                },
            },
            column: {
                events: {
                    legendItemClick: function () {
                        return false;
                    }
                },
                pointWidth: 25,
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
            shared: true,
            animation: false,
            formatter: function () {
                if (!animationComplete) return false;
                var x = this.x;
                var s = '';
                $.each(this.points, function (i, point) {
                    var label = i === 0 ? fundLabels[x] : benchmarkLabels[x];
                    s += point.series.name + ': Situation ' + label + ', Payoff <b>' + formatPayoffCurrency(point.y) + '</b><br>';
                });
                return s;
            },
        },
        legend: {
            backgroundColor: '#f8f9fa',
            enabled: true,
            squareSymbol: false,
            symbolHeight: 10,
            symbolWidth: 10,
            x: 0,
            y: 10,
            zIndex: 100,
            floating: true,
            shadow: false,
            itemStyle: {
                fontSize: '20px',
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
            pointPlacement: -0.04,
            pointRange: 1,
            clip: false,
            zIndex: 1,
            id: 'main',
            dataLabels: {
                enabled: false,
                formatter: function() {
                    return this.point.label;
                },
                style: {
                    fontSize: '14px',
                    color: '#00BFFF',
                    fontWeight: 'normal',
                    textOutline: 'none',
                },
                verticalAlign: 'bottom',
                align: 'center',
                y: 5,  // pushes label below the bar
            }
        },
        {
            name: 'Asset B',
            data: chartBenchmark,
            color: '#808080',
            zones: lossGainZones,
            zoneAxis: 'y',
            borderColor: assetBBorderColor,
            borderWidth: assetBorderWidth,
            pointPlacement: 0.04,
            pointRange: 1,
            clip: false,
            zIndex: 0,
            dataLabels: {
                enabled: false,
                formatter: function() {
                    return this.point.label;
                },
                style: {
                    fontSize: '14px',
                    color: '#808080',
                    fontWeight: 'normal',
                    textOutline: 'none',
                },
                verticalAlign: 'bottom',
                align: 'center',
                y: 5,
            }
        },
        ]
    });
});

// Write function to record time spent on tooltip
let inX = -10;
let outX = -10;

let startTime = -10;
let timeSpent = [];



/*
recordTimeSpent(tmpYear) {
    if (lastYear != tmpYear) {
        
        let endTime = new Date().getTime();
    } else {
        return;
    }
}


        function updateTimeSpent() {
            let endTime = new Date().getTime();
            let tmpTimeSpent = endTime - startTime;
            timeSpent.push(tmpTimeSpent);
            startTime = endTime;

            document.getElementById('sequentialTimeSpent').value = timeSpent; // Update the hidden field with the time spent
        }
*/
