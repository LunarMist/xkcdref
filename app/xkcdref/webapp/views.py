import math

import simplejson
from flask import render_template, Response

from xkcdref.webapp import app, db, cache
from xkcdref import settings

CACHE_KEY_REFERENCE_COUNT = 'reference_count'
CACHE_KEY_STATS_CONTEXT = 'stats_context'

MSG_SUCCESS = "Success"


@app.route('/')
def index_page():
    return render_template('index.html', track=settings.ENABLE_TRACKING)


@app.route('/statistics/')
def xkcd_statistics():
    cached_reference_count = cache.get(CACHE_KEY_REFERENCE_COUNT)
    current_reference_count = db.get_xkcd_event_count()

    # If nothing changed since the last xkcd reference, load cached json
    if cached_reference_count and int(cached_reference_count) == current_reference_count:
        cached_stats_context = cache.get_json(CACHE_KEY_STATS_CONTEXT)
        if cached_stats_context:
            return render_template('stats.html', track=settings.ENABLE_TRACKING, **cached_stats_context)

    # Get general statistics
    unique_comics_referenced, unique_subreddit_referencers, unique_user_referencers, total_reference_count, \
        mean_references, variance = db.get_xkcd_global_stats()
    std_dev = math.sqrt(variance)

    # Build top user references list
    top_referencers = []
    user_rank = 1
    for user, count in db.get_top_user_referencers(5):
        top_referencers.append([user_rank, user, count])
        user_rank += 1

    # Get list of unique subreddits
    unique_subreddits_list = [s[0] for s in db.get_unique_subreddits()]
    unique_subreddits_list = list(sorted(unique_subreddits_list))

    # Get comic title info
    comic_titles = []
    for comic_id, title in db.get_xkcd_comic_titles():
        comic_titles.append('%d: %s' % (comic_id, title))

    # Get comic rankings
    comic_rankings = []
    for rank, comic_id, title, comic_count, comic_percentage, num_std_dev in get_rankings():
        comic_rankings.append([rank, [comic_id, title], comic_count, comic_percentage, num_std_dev])

    context = {
        'unique_comics_count': unique_comics_referenced,
        'unique_subreddits_count': unique_subreddit_referencers,
        'unique_referencers': unique_user_referencers,
        'total_count': total_reference_count,
        'mean_value': mean_references,
        'std_deviation': std_dev,
        'top_users': top_referencers,
        'unique_subreddits': unique_subreddits_list,
        'comic_titles': simplejson.dumps(comic_titles),
        'comic_rankings': comic_rankings,
    }

    # Cache the new values
    cache.set(CACHE_KEY_REFERENCE_COUNT, current_reference_count)
    cache.set_json(CACHE_KEY_STATS_CONTEXT, context)

    return render_template('stats.html', track=settings.ENABLE_TRACKING, **context)


@app.route('/backrefs/')
def xkcd_backreferences():
    # Get comic title info
    comic_titles = []
    for comic_id, title in db.get_xkcd_comic_titles():
        comic_titles.append({
            'value': comic_id,
            'label': str(comic_id) + ': ' + title
        })

    context = {
        'comic_titles': simplejson.dumps(comic_titles),
    }

    return render_template('backrefs.html', track=settings.ENABLE_TRACKING, **context)


@app.route('/hb/')
def hb_page():
    return MSG_SUCCESS, 200


@app.route('/downloads/events/')
def download_data():
    def generate():
        yield 'comic_id, time, subreddit, user, link\n'
        for cols in db.get_xkcd_events():
            cols = [unicode(col) for col in cols]
            yield ','.join([col.encode('utf-8') for col in cols]) + '\n'

    headers = {
        'Content-Disposition': 'attachment; filename="xkcd_ref_data.csv"'
    }

    return Response(generate(), mimetype='text/csv', headers=headers)


@app.route('/downloads/ranking/')
def download_rankings():
    def generate():
        yield 'rank, comic, count, % total, # std dev. from the mean\n'
        for rank, comic_id, title, comic_count, comic_percentage, num_std_dev in get_rankings():
            full_title = '%d: %s' % (comic_id, title)
            full_title = escape_csv_field(full_title)

            cols = [rank, full_title, comic_count, comic_percentage, num_std_dev]
            cols = [unicode(col) for col in cols]
            yield ','.join([col.encode('utf-8') for col in cols]) + '\n'

    headers = {
        'Content-Disposition': 'attachment; filename="xkcd_rankings.csv"'
    }

    return Response(generate(), mimetype='text/csv', headers=headers)


def get_rankings():
    """
    Get xkcd rankings.
    :return: A generator of tuples of the format (rank, comic_id, title, comic_count, comic_percentage,
            number_std_dev_from_the_mean) ordered by rank.
    """
    _, _, _, _, mean_references, variance = db.get_xkcd_global_stats()
    std_dev = math.sqrt(variance)
    rank = 1

    for comic_id, title, comic_count, comic_percentage in db.get_xkcd_stats():
        yield rank, comic_id, title, comic_count, comic_percentage, (comic_count - mean_references) / std_dev
        rank += 1


def escape_csv_field(field):
    """
    Escape a csv field.
    :param field: The CSV field to escape.
    :return: A CSV-safe field.
    """
    quote_escape = field.find(',') != -1 or field.find('"') != -1
    field = field.replace('"', '""')
    if quote_escape:
        return '"%s"' % field
    else:
        return field
