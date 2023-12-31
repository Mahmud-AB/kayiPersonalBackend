(function ($) {
    'use strict';
    window.chartColors = {
        red: 'rgb(255, 99, 132)',
        orange: 'rgb(255, 159, 64)',
        yellow: 'rgb(255, 205, 86)',
        green: 'rgb(75, 192, 192)',
        blue: 'rgb(54, 162, 235)',
        purple: 'rgb(153, 102, 255)',
        grey: 'rgb(201, 203, 207)'
    };

    $(function () {
        if ($(".dashboard-progress-1").length) {
            const parsentage = (g_toc / g_to) == Infinity ? 0 : (g_toc / g_to);
            $('.dashboard-progress-1').circleProgress({
                value: parsentage > 0 ? parsentage : 100,
                size: 125,
                thickness: 7,
                startAngle: 80,
                fill: {
                    gradient: parsentage > 0 ? ["#7922e5", "#1579ff"] : ["#e2e2e2", "#e2e2e2"]
                }
            });
        }
        if ($(".dashboard-progress-3").length) {
            const parsentage = (total_visitor_products / total_product_count) == Infinity ? 0 : (total_visitor_products / total_product_count);
            $('.dashboard-progress-3').circleProgress({
                value: parsentage > 0 ? parsentage : 100,
                size: 125,
                thickness: 7,
                startAngle: 10,
                fill: {
                    gradient: parsentage > 0 ? ["#f76b1c", "#fad961"] : ["#e2e2e2", "#e2e2e2"]
                }
            });
        }

        if ($("#page-view-analytic").length) {
            var tempDataValue = []
            var tempDataDate = []
            for (var i = 0; i < g_graph1.length; i++) {
                tempDataValue.push(g_graph1[i][0])
                tempDataDate.push(g_graph1[i][1])
            }
            var barChartCanvas = $("#page-view-analytic").get(0).getContext("2d");
            var config = {
                type: 'line',
                data: {
                    labels: tempDataDate,
                    datasets: [
                        {label: 'Order Compete last 30 days', fill: false, backgroundColor: window.chartColors.blue, borderColor: window.chartColors.blue, data: tempDataValue,}
                    ]
                },
                options: {
                    responsive: true,
                    title: {display: true, text: ''},
                    tooltips: {mode: 'index', intersect: false,},
                    hover: {mode: 'nearest', intersect: true},
                    scales: {xAxes: [{display: true, scaleLabel: {display: true, labelString: 'Days'}}], yAxes: [{display: true, scaleLabel: {display: true, labelString: 'Complete Order'}}]}
                }
            };

            var barChart = new Chart(barChartCanvas, config);
        }

        if ($("#page-view-analytic-filter").length) {
            var tempDataValue = []
            var tempDataDate = []
            for (var i = 0; i < graph1_diff.length; i++) {
                tempDataValue.push(graph1_diff[i][0])
                tempDataDate.push(graph1_diff[i][1])
            }
            var config = {
                type: 'line',
                data: {
                    labels: tempDataDate,
                    datasets: [
                        {label: 'Order Compete', fill: false, backgroundColor: window.chartColors.blue, borderColor: window.chartColors.blue, data: tempDataValue,}
                    ]
                },
                options: {
                    responsive: true,
                    title: {display: true, text: ''},
                    tooltips: {mode: 'index', intersect: false,},
                    hover: {mode: 'nearest', intersect: true},
                    scales: {xAxes: [{display: true, scaleLabel: {display: true, labelString: 'Days'}}], yAxes: [{display: true, scaleLabel: {display: true, labelString: 'Complete Order'}}]}
                }
            };

            var barChart = new Chart($("#page-view-analytic-filter").get(0).getContext("2d"), config);
        }

    });
})(jQuery);