$(document).ready(function () {
    $("#search_comic_id").autocomplete({
        source: backrefs.comic_titles
    });

    var performSearch = function () {
        var url = "/api/backrefs/";
        var params = {};

        $('.search_param').each(function () {
            if (this.value !== null && this.value.trim() !== '') {
                params[this.id.replace("search_", "")] = this.value;
            }
        });

        if (window.history.replaceState) {
            window.history.replaceState('', '', '/backrefs/?' + $.param(params));
        }

        $.get(url, params).done(function (response) {
            data = response['data'];
            truncated = response['truncated'];

            if (data.length == 0) {
                $("#backref_results").html("Zero results returned");
                return;
            }

            var t = "<table class='table table-striped table-bordered table-hover' id='backref_results_table'>";
            t += "<thead><tr>";
            t += "<th>Comic</th>";
            t += "<th>Date</th>";
            t += "<th>Subreddit</th>";
            t += "<th>User</th>";
            t += "<th>Link</th>";
            t += "</tr></thead><tbody>";
            for (var i in data) {
                t += "<tr>";
                t += "<td><a href='https://xkcd.com/" + data[i].comic_id + "'>" + backrefs.comic_titles[data[i].comic_id - 1]['label'] + "</a></td>";
                t += "<td>" + moment.unix(data[i].time).format('MMM Do, YYYY hh:mm a') + "</td>";
                t += "<td><a href='https://reddit.com/r/" + data[i].subreddit + "'>/r/" + data[i].subreddit + "</a></td>";
                t += "<td><a href='https://reddit.com/u/" + data[i].user + "'>/u/" + data[i].user + "</a></td>";
                t += "<td><a href='" + data[i].link + "'>Permalink</a></td>";
                t += "</tr>";
            }
            t += "</tbody></table>"

            if (truncated > 0) {
                $("#error").html(truncated + " results truncated");
            }
            $("#backref_results").html(t);
            $('#backref_results_table').dataTable({
                "sDom": "<'row'<'col-md-6'l><'col-md-6'f>r>t<'row'<'col-md-6'i><'col-md-6'p>>",
                "sPaginationType": "bootstrap",
                "oLanguage": {
                    "sLengthMenu": "_MENU_ records per page"
                }
            });
        }).fail(function (error) {
            $("#backref_results").html('An unknown error has occured.');
        });
    };

    $("#search").click(function () {
        $("#error").html("");

        var subreddit = $('#search_subreddit').val();
        var user = $('#search_user').val();
        var comicId = $('#search_comic_id').val();
        if (subreddit !== '' || user !== '' || comicId != '') {
            $("#backref_results").html("Loading...");
            performSearch();
        }
    });

    function getParameterByName(name) {
        name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
        var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
            results = regex.exec(location.search);
        return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
    }

    var hlink_subreddit = getParameterByName('subreddit');
    var hlink_user = getParameterByName('user');
    var hlink_comic_id = getParameterByName('comic_id');

    $('#search_subreddit').val(hlink_subreddit);
    $('#search_user').val(hlink_user);
    $('#search_comic_id').val(hlink_comic_id);

    if (hlink_subreddit !== '' || hlink_user !== '' || hlink_comic_id !== '') {
        $("#search").click();
    }
});