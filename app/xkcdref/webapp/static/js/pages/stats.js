// Radialize the colors
Highcharts.getOptions().colors = Highcharts.map(Highcharts.getOptions().colors, function (color) {
    return {
        radialGradient: {cx: 0.5, cy: 0.3, r: 0.7},
        stops: [
            [0, color],
            [1, Highcharts.Color(color).brighten(-0.3).get('rgb')] // darken
        ]
    };
});

var graphChart = function (targetDiv, chartTitle, chartData, chartPointFormat, chartOnClick) {
    // Build the chart
    return new Highcharts.Chart({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            renderTo: targetDiv
        },
        title: {
            text: chartTitle
        },
        tooltip: {
            pointFormat: chartPointFormat
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    color: '#000000',
                    connectorColor: '#000000',
                    formatter: function () {
                        return '<b>' + this.point.name + '</b>: ' + this.percentage.toFixed(2) + ' %';
                    }
                }
            }
        },
        series: [{
            type: 'pie',
            name: 'Count',
            data: chartData,
            point: {
                events: {
                    click: function () {
                        if (chartOnClick !== null) {
                            chartOnClick(this);
                        }
                    }
                }
            }
        }],
        credits: {
            enabled: false
        }
    });
};

$(document).ready(function () {
    var subDetailsChart = null,
        comicDetailsChart = null;

    var graphSubDetails = function () {
        var sub = $("#select_subreddit").val();
        var params = {'subreddit': sub};
        $.get("/api/breakdown/sub/", params).done(function (data) {
            var ele = $("#subreddit_breakdown_details");
            if (ele.html() === '') {
                onClick = function (chart) {
                    if (chart.name[0] !== 'o') {
                        window.open('https://xkcd.com/' + chart.name);
                    }
                };
                subDetailsChart = graphChart('subreddit_breakdown_details', 'References for /r/' + sub, data, '{series.name}: <b>{point.percentage:.1f}% ({point.y})</b>', onClick);
            } else {
                subDetailsChart.series[0].setData(data);
                subDetailsChart.setTitle({text: 'References for /r/' + sub});
            }
        });
    };

    var graphComicDetails = function (ui) {
        var comic_id = ui.item.value.split(":", limit = 1)[0];
        var value = ui.item.value;
        var params = {'comic_id': comic_id};
        if (comic_id !== null) {
            $.get("/api/breakdown/comic/", params).done(function (data) {
                var ele = $("#comic_breakdown_details");
                if (ele.html() === '') {
                    comicDetailsChart = graphChart('comic_breakdown_details', 'References for ' + value, data, '{series.name}: <b>{point.percentage:.1f}% ({point.y})</b>', null);
                } else {
                    comicDetailsChart.series[0].setData(data);
                    comicDetailsChart.setTitle({text: 'References for ' + value});
                }
            });
        }
    };

    // Main table
    $('#basic_stats').dataTable({
        "sDom": "<'row'<'col-md-6'l><'col-md-6'f>r>t<'row'<'col-md-6'i><'col-md-6'p>>",
        "sPaginationType": "bootstrap",
        "oLanguage": {
            "sLengthMenu": "_MENU_ records per page"
        }
    });

    // Comic breakdown
    $("#search_comic").autocomplete({
        source: stats.comic_titles,
        select: function (event, ui) {
            graphComicDetails(ui);
        }
    });

    // Subreddit breakdown
    $.get("/api/distribution/sub/").done(function (data) {
        graphChart('subreddit_breakdown', 'References by subreddit', data, '{series.name}: <b>{point.percentage:.1f}%</b>', null);
    });

    // Sub details
    graphSubDetails();
    $("#select_subreddit").change(function (event) {
        graphSubDetails();
    });
});