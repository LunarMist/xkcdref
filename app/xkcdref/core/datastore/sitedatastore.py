import sqlite3


class SimpleDataStore(object):
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    def open(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute(self, *args, **kwargs):
        self.open()
        c = self.conn.cursor()
        c.execute(*args, **kwargs)
        return c

    def commit(self):
        if self.conn:
            self.conn.commit()


class SiteDataStore(object):
    def __init__(self, database_path):
        self.database_path = database_path
        self.datastore = SimpleDataStore(self.database_path)

    def get_xkcd_events(self):
        """
        Get all xkcd events.
        :return: A generator of tuples of the format (comic_id, time, subreddit, user, link)
        """
        cursor = self.datastore.execute(
            'SELECT comic_id, time, subreddit, user, link FROM xkcd_comic_references'
        )

        for v in cursor:
            yield v

    def get_xkcd_stats(self):
        """
        Get per-comic statistics.
        :return: A generator of tuples of the format (comic_id, title, comic_count, comic_percentage)
        """
        cursor = self.datastore.execute("""
            SELECT rc.comic_id, title, comic_count, comic_percentage
            FROM references_counts rc LEFT JOIN xkcd_comic_meta xcm ON rc.comic_id = xcm.comic_id
            ORDER BY comic_count DESC
        """)

        for v in cursor:
            yield v

    def get_top_user_referencers(self, top_count):
        """
        Get user rankings based on reference count per user.
        :param top_count: The max number of users to return.
        :return: A generator of tuples of the format (user, reference_count) in descending order of reference count.
        """
        cursor = self.datastore.execute(
            'SELECT user, COUNT(*) AS refs FROM xkcd_comic_references GROUP BY user ORDER BY refs DESC LIMIT ?',
            (top_count,)
        )

        for v in cursor:
            yield v

    def get_top_subreddit_referencers(self, top_count=None):
        """
        Get subreddit rankings based on reference count per subreddit.
        :param top_count: The max number of users to return. Pass `None` for no limit.
        :return: A generator of tuples of the format (subreddit, reference_count) in descending order of reference count.
        """
        if top_count is None:
            cursor = self.datastore.execute(
                'SELECT subreddit, COUNT(*) AS refs FROM xkcd_comic_references GROUP BY subreddit ORDER BY refs DESC'
            )
        else:
            cursor = self.datastore.execute(
                'SELECT subreddit, COUNT(*) AS refs FROM xkcd_comic_references GROUP BY subreddit ORDER BY refs DESC LIMIT ?',
                (top_count,)
            )

        for v in cursor:
            yield v

    def get_subreddit_breakdown(self, subreddit):
        """
        Get comic reference count filtered by a subreddit.
        :param subreddit: The subreddit to filter by.
        :return: A generator of tuples of the format (comic_id, reference_count) in descending order.
        """
        cursor = self.datastore.execute(
            'SELECT comic_id, COUNT(*) FROM xkcd_comic_references WHERE subreddit = ? GROUP BY comic_id ORDER BY COUNT(*) DESC',
            (subreddit,)
        )

        for v in cursor:
            yield v

    def get_comic_breakdown(self, comic_id):
        """
        Get subreddit reference count filetered by comic id.
        :param comic_id: The comic id to filter by.
        :return: A generator of tuples of the format (subreddit, reference_count) in descending order.
        """
        cursor = self.datastore.execute(
            'SELECT subreddit, COUNT(*) AS count FROM xkcd_comic_references WHERE comic_id = ? GROUP BY subreddit ORDER BY COUNT(*) DESC',
            (comic_id,)
        )

        for v in cursor:
            yield v

    def get_xkcd_event_count_by_subreddit(self, subreddit):
        """
        Get the number of references made by subreddit.
        :param subreddit: The subreddit's name.
        :return: The number of references made in the spcified subreddit.
        """
        cursor = self.datastore.execute(
            'SELECT COUNT(*) FROM xkcd_comic_references WHERE subreddit = ?',
            (subreddit,)
        )

        return cursor.fetchone()[0]

    def get_xkcd_event_count_by_comic_id(self, comic_id):
        """
        Get the number of references made by comic id.
        :param comic_id: The comic id.
        :return: The number of references made for a specific comic.
        """
        cursor = self.datastore.execute(
            'SELECT COUNT(*) FROM xkcd_comic_references WHERE comic_id = ?',
            (comic_id,)
        )

        return cursor.fetchone()[0]

    def get_unique_subreddits(self):
        """
        Get the number of unique subreddits where references have been made.
        :return: The number of unique subreddits where references have been made.
        """
        cursor = self.datastore.execute(
            'SELECT DISTINCT(subreddit) FROM xkcd_comic_references'
        )

        for v in cursor:
            yield v

    def get_xkcd_event_count(self):
        """
        Get the number of xkcd references that have been made to date.
        :return: The number of xkcd references that have been made to date.
        """
        cursor = self.datastore.execute(
            'SELECT COUNT(*) FROM xkcd_comic_references'
        )

        return cursor.fetchone()[0]

    def get_xkcd_global_stats(self):
        """
        Get global xkcd statistics.
        :return: A tuple of the format (unique_comics_referenced, unique_subreddit_referencers, unique_user_referencers,
                total_reference_count, mean_references, variance)
        """
        cursor = self.datastore.execute("""
            SELECT * FROM (
                SELECT
                    COUNT(DISTINCT(comic_id)) AS unique_comics_referenced,
                    COUNT(DISTINCT(subreddit)) AS unique_subreddit_referencers,
                    COUNT(DISTINCT(user)) AS unique_user_referencers
                FROM
                    xkcd_comic_references
            ),(
                SELECT
                    SUM(comic_count) AS total_reference_count,
                    AVG(comic_count) AS mean_references,
                    AVG((comic_count - (SELECT AVG(comic_count) FROM references_counts)) *
                        (comic_count - (SELECT AVG(comic_count) FROM references_counts))) AS variance
                FROM
                    references_counts
            )
        """)

        return cursor.fetchone()

    def get_xkcd_comic_titles(self):
        """
        Get comic id / comic title pairs.
        :return: A generator of tuples of the the format (comic_id, comic_title).
        """
        cursor = self.datastore.execute(
            'SELECT comic_id, title FROM xkcd_comic_meta'
        )

        for v in cursor:
            yield v

    def get_backreferences(self, subreddit, username, comic_id):
        """
        Get the references made, filtered by subreddit, user and comic id.
        :param subreddit: The subreddit to filter. Case insensitive.
        :param username: The username to filter by. Case insensitive.
        :param comic_id: The comic id to filter by.
        :return: A generator of tuples of the format (comic_id, time, subreddit, user, link) subjected to the
                provided filter parameters.
        """
        built_query = 'SELECT comic_id, time, subreddit, user, link FROM xkcd_comic_references WHERE '
        conditions = []
        params = []

        if subreddit:
            conditions.append('subreddit = ? COLLATE NOCASE')
            params.append(subreddit)

        if username:
            conditions.append('user = ? COLLATE NOCASE')
            params.append(username)

        if comic_id:
            conditions.append('comic_id = ? COLLATE NOCASE')
            params.append(comic_id)

        built_query += ' AND '.join(conditions)

        cursor = self.datastore.execute(built_query, params)

        for v in cursor:
            yield v
