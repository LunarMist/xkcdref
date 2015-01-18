import simplejson
from flask import Response, request

from xkcdref.webapp import app, db

MAX_BACKREFS = 500


@app.route('/api/distribution/sub/')
def api_sub_distribution():
    total_ref_count = db.get_xkcd_event_count()
    ref_generator = db.get_top_subreddit_referencers()
    subreddits = prettify_reference_count_list(total_ref_count, ref_generator,
                                               threshold_percentage=0.01, max_ref_inclusion=9999999)

    data = simplejson.dumps(subreddits)
    return Response(response=data, mimetype='application/json')


@app.route('/api/breakdown/sub/')
def api_sub_breakdown():
    subreddit = request.args.get('subreddit')
    comics = []
    if subreddit:
        total_ref_count = db.get_xkcd_event_count_by_subreddit(subreddit)
        if total_ref_count > 0:
            ref_generator = db.get_subreddit_breakdown(subreddit)
            comics = prettify_reference_count_list(total_ref_count, ref_generator)

    data = simplejson.dumps(comics)
    return Response(response=data, mimetype='application/json')


@app.route('/api/breakdown/comic/')
def api_comic_breakdown():
    comic_id = request.args.get('comic_id')
    subs = []
    if comic_id:
        total_ref_count = db.get_xkcd_event_count_by_comic_id(comic_id)
        if total_ref_count > 0:
            ref_generator = db.get_comic_breakdown(comic_id)
            subs = prettify_reference_count_list(total_ref_count, ref_generator)

    data = simplejson.dumps(subs)
    return Response(response=data, mimetype='application/json')


@app.route('/api/backrefs/')
def api_backreferences():
    sub = request.args.get('subreddit')
    user = request.args.get('user')
    comic = request.args.get('comic_id')
    refs = []

    if comic and comic.isdigit():
        comic = int(comic)
    else:
        comic = None

    if sub or user or comic:
        for comic_id, time, subreddit, username, link in db.get_backreferences(sub, user, comic):
            refs.append({
                'comic_id': comic_id,
                'time': time,
                'subreddit': subreddit,
                'user': username,
                'link': link,
            })

    data = simplejson.dumps({
        'data': refs[:MAX_BACKREFS],
        'truncated': len(refs) - MAX_BACKREFS if len(refs) > MAX_BACKREFS else 0,
    })
    return Response(response=data, mimetype='application/json')


def prettify_reference_count_list(total_ref_count, ref_generator, threshold_percentage=0.005, max_ref_inclusion=30):
    included_count = 0
    other_ref_count = 0
    references = []

    for name, ref_count in ref_generator:
        if ref_count / float(total_ref_count) < threshold_percentage or included_count > max_ref_inclusion:
            other_ref_count += ref_count
            threshold_percentage = round(threshold_percentage, 2)
        else:
            references.append([str(name), ref_count])
            included_count += 1

    if other_ref_count > 0:
        references.append(['other (&lt; %d%% ea.)' % (threshold_percentage * 100), other_ref_count])

    return references
