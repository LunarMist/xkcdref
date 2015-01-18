import os
import sys

import simplejson

from xkcdref.core.datastore.sitedatastore import SimpleDataStore


def create(datastore):
    datastore.execute("""
        CREATE TABLE IF NOT EXISTS ignored_users (
            bot_name TEXT,
            target_name TEXT,
            UNIQUE(bot_name, target_name) ON CONFLICT IGNORE
        );
        """)

    datastore.execute("""
        CREATE TABLE IF NOT EXISTS xkcd_comic_references (
            comic_id INTEGER,
            time INTEGER NOT NULL,
            subreddit TEXT,
            user TEXT,
            link TEXT,
            UNIQUE(comic_id, subreddit, user, link) ON CONFLICT IGNORE
        );
        """)

    datastore.execute("""
        CREATE TABLE IF NOT EXISTS xkcd_comic_meta (
            comic_id INTEGER PRIMARY KEY,
            json TEXT,
            title TEXT,
            hash_avg TEXT,
            hash_d TEXT,
            hash_p TEXT
        );
        """)

    datastore.execute("""
        CREATE VIEW IF NOT EXISTS references_counts AS
            SELECT
                comic_id,
                0 AS comic_count,
                0.0 AS comic_percentage
            FROM
                xkcd_comic_meta
            WHERE comic_id NOT IN (
                SELECT DISTINCT(comic_id) FROM xkcd_comic_references
            )
            UNION
            SELECT
                comic_id,
                COUNT(*) AS comic_count,
                (COUNT(*) * 100.0) / (SELECT COUNT(*) FROM xkcd_comic_references) AS comic_percentage
            FROM
                xkcd_comic_references
            GROUP BY
                comic_id
        ;
        """)

    datastore.commit()


def main():
    # Check for path
    if not len(sys.argv) == 2:
        print 'format: python', sys.argv[0], '<old db path>'
        sys.exit(0)

    old_db_location = sys.argv[1]
    new_db_location = old_db_location + '.new'

    print 'Begin conversion'
    print 'Old:', old_db_location
    print 'New:', new_db_location

    if os.path.exists(new_db_location):
        os.remove(new_db_location)
        print 'Deleted new db'

    db_old = SimpleDataStore(old_db_location)
    db_new = SimpleDataStore(new_db_location)

    print 'Creating db tables'
    create(db_new)

    print 'Copying ignore table'
    cursor = db_old.execute('SELECT bot_name, target_name from stats_ignore')
    for a, b in cursor:
        db_new.execute('INSERT INTO ignored_users VALUES (?, ?)', (a, b))
    db_new.commit()

    print 'Copying xkcd meta table'
    cursor = db_old.execute('SELECT id, json, hash_avg, hash_d, hash_p FROM stats_xkcd_meta')
    for a, b, c, d, e in cursor:
        j = simplejson.loads(b)
        db_new.execute('INSERT INTO xkcd_comic_meta VALUES (?, ?, ?, ?, ?, ?)', (a, b, j['title'], c, d, e))
    db_new.commit()

    print 'Copying xkcd references table'
    cursor = db_old.execute('SELECT comic_id, time, subreddit, user, link FROM stats_xkcd_event')
    for a, b, c, d, e in cursor:
        db_new.execute('INSERT INTO xkcd_comic_references VALUES (?, ?, ?, ?, ?)', (a, b, c, d, e))
    db_new.commit()

    print 'Performing VACUUM'
    db_new.execute('VACUUM')

    print 'Closing connections...'
    db_old.close()
    db_new.close()

    print 'Conversion finished'


if __name__ == '__main__':
    main()
