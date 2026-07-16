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

        var absMaxFund = Math.max(...DataFund.map(Math.abs)); // Get absolute maximum from DataFund
        var absMaxBenchmark = Math.max(...DataBenchmark.map(Math.abs)); // Get absolute maximum from DataBenchmark

        var dynamicMaxValue = Math.max(absMaxFund, absMaxBenchmark); // Choose the larger of the two
        var dynamicMinValue = -dynamicMaxValue; // Symmetric minimum value

/// Then, this creates the graph
$(function () {
    Highcharts.chart('contr2', {
        chart: {
            backgroundColor: '#f8f9fa',
            type: 'column',
            height: 400,
            marginLeft: 70,
            marginRight: 30,
            marginBottom: 100,
            marginf: 55,
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
                    fontSize: '15px'
                },
                text: 'Payoff'
            },
            labels: {
                style: {
                    fontSize: '14px'
                },
                enabled:true,
                formatter: function(){
                    return this.value;
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
                animation: {
                    duration: 000
                },
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
            formatter: function () {
                if (!animationComplete) return false;
                var x = this.x;
                var s = '';
                $.each(this.points, function (i, point) {
                    var label = i === 0 ? fundLabels[x] : benchmarkLabels[x];
                    s += point.series.name + ': Situation ' + label + ', Payoff <b>' + Highcharts.numberFormat(point.y, 2, '.', ',') + '</b><br>';
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
                fontSize: '20px'
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
