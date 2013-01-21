import sqlite3
import pickle
import datetime


class PickledDict(dict):
    pass


def adapt_pickled_dict(pidi):
    return pickle.dumps(pidi)


def convert_pickled_dict(s):
    return pickle.loads(s)


class Cache(object):

    def __init__(self, dsn_or_dbh, rc):
        """
        The Blog Cache.

        A facade to a SQLite3 storage.

        Caches converted text of blog articles, e.g. after Markdown conversion,
        along with cardinal attributes. Each of these attributes is stored in
        its own column and can later be queried in a SELECT:

        - ``id``: Auto ID. Unique.
        - ``relfn``: Unique. Path and filename of the article relative to the
            content directory.
        - ``slug``: Unique. String as used in URL.
        - ``pubdate_utc``: Timestamp of publication date. Store this in UTC so
            we can sort by pubdate independent of timezones; SQLite does not
            handle timezones.
        - ``title``: String as title.
        - ``category``: String as category. (The schema is not fully
            normalised.)
        - ``author``: String as author.
        - ``meta``: BLOB as pickled dict.
        - ``summary``: Converted text of summary
        - ``body``: Converted text of complete article
        - ``cache_time``: Timestamp of when this article was cached. We compare
            this against the article's file time to determine whether the entry
            is outdated or not.

        The datastructure to add an article must contain one more field:
        ``tags``, which is a list of strings with the tags.

        **How to use**

        1. Create database schema: :meth:`create_tables`
        2. Initialise cache: :meth:`add_all`
           This method can be called everytime you wish to rewrite the cache
           completely.
        3. To add a single article: :meth:`add`

        Compare items in the cache with the original article files and
        determine which have to be updated: :meth:`prepare`. This method also
        removes stale items.

        Retrieve data with one of the ``get_*`` or ``list_*`` or ``count_*``-
        methods.

        Updates first delete the article, then add the new one. This creates
        a new ID for that article. We do not believe this ID is useful outside
        the cache, so changing it does not have a big impact. Deleting then
        inserting is much easier than to update the article in-place and keep
        the tags in sync.

        :param dsn_or_dbh: Either a DSN (str) or an already established
            connection. **Important**: The connection must have been
            opened with ``detect_types=sqlite3.PARSE_DECLTYPES``. We rely
            on SQLite to convert to Python's datetime objects.
        :param rc: Dict with additional settings. Not used yet.
        """
        if isinstance(dsn_or_dbh, str):
            self.dsn = dsn_or_dbh
            self.dbh = sqlite3.connect(dsn_or_dbh,
                detect_types=sqlite3.PARSE_DECLTYPES)
        else:
            self.dsn = None
            self.dbh = dsn_or_dbh
        self.dbh.row_factory = sqlite3.Row
        sqlite3.register_adapter(PickledDict, adapt_pickled_dict)
        sqlite3.register_converter('PickledDict', convert_pickled_dict)
        self.rc = rc if rc else {}
        self._tags = {}
        self._am_i()

    def _am_i(self):
        q = "SELECT id FROM blog_article LIMIT 1"
        cur = self.dbh.cursor()
        try:
            cur.execute(q)
        except sqlite3.OperationalError:
            self.create_tables()

    def prepare(self, files, dry_run=False):
        """
        Prepares cache for adding/updating articles.

        Compares a list of files with the cached articles and determines
        whether a file changes an existing cache entry, has to be cached newly
        or which cache entry has to be deleted, because the source file does
        not exist any more.

        This method returns the list of files which need to be cached. It also
        changes the cache: it removes obsolete entries, and it removes out of
        date entries, so they can be cached freshly.

        :param files: Mapping of (relative) filenames (str) to file times
            (datetime).
        :param dry_run: If True, just prepares the file list and does not
            change the cache.
        :returns: List of filenames which need to be cached.
        """
        # Determine state of files
        cur = self.dbh.cursor()
        q = "SELECT id, relfn, cache_time FROM blog_article"
        to_del = []
        to_update = []
        seen = []
        for row in cur.execute(q):
            if row['relfn'] in files:
                # If cached item is older than file, we need to update it
                if row['cache_time'] < files[row['relfn']]:
                    to_update.append(row['relfn'])
                    # Updating means to delete the cached item and add the new
                    to_del.append((row['id'], ))  # tuple for executemany
            else:
                # Cached file does not exist anymore, remove from cache
                to_del.append((row['id'], ))  # tuple for executemany
            seen.append(row['relfn'])
        seen = set(seen)
        proposed = set(files.keys())
        to_add = (proposed - seen) | set(to_update)
        if not dry_run:
            self.delete(to_del)
        return to_add

    def get_article_by_id(self, id_):
        q = "SELECT id, meta, body FROM blog_article" \
            " WHERE id=?"
        cur = self.dbh.cursor()
        cur.execute(q, (id_, ))
        return dict(cur.fetchone())

    def get_article_by_relfn(self, relfn):
        q = "SELECT id, meta, body FROM blog_article" \
            " WHERE relfn=?"
        cur = self.dbh.cursor()
        cur.execute(q, (relfn, ))
        return dict(cur.fetchone())

    def get_article_by_slugparts(self, slugparts):
        """
        Returns article identified by its slug.

        Slug is given as list of its parts. The blog may allow to
        store the article in nested directories.

        For simplicity, we store the slug's hierarchy as materialised paths.
        """
        q = "SELECT id, meta, body FROM blog_article" \
            " WHERE slug=?"
        cur = self.dbh.cursor()
        cur.execute(q, ("/".join(slugparts), ))
        return dict(cur.fetchone())

    def count_articles(self):
        q = "SELECT count(*) FROM blog_article"
        cur = self.dbh.cursor()
        cur.execute(q)
        return cur.fetchone()[0]

    def get_index_page(self, page):
        """
        Returns one page of list of articles in reverse chronological order.

        The list has two fields: ``id`` and ``meta``, the latter contains
        key ``summary``.

        The number of returned rows is determined by the cache's property
        ::prop:`page_size`.

        :param page: Number of page (1..n)
        """
        if page < 1:
            page = 1
        offset = self.page_size * (page - 1)
        q = "SELECT id, meta FROM blog_article ORDER BY pubdate_utc DESC" \
            " LIMIT ? OFFSET ?"
        cur = self.dbh.cursor()
        cur.execute(q, (self.page_size, offset))
        return cur.fetchall()

    def get_year_page(self, year, page):
        """
        Lists articles in given year.

        Details see :meth:`get_index_page`.
        """
        if page < 1:
            page = 1
        offset = self.page_size * (page - 1)
        q = "SELECT id, meta FROM blog_article" \
            " WHERE pubdate_utc >= :d AND pubdate_utc < date(:d, '+1 year')" \
            " ORDER BY pubdate_utc DESC" \
            " LIMIT :lim OFFSET :off"
        d = datetime.date(year, 1, 1)
        cur = self.dbh.cursor()
        cur.execute(q, {'d': d, 'lim': self.page_size, 'off': offset})
        return cur.fetchall()

    def get_month_page(self, year, month, page):
        """
        Lists articles in given year and month.

        Details see :meth:`get_index_page`.
        """
        if page < 1:
            page = 1
        offset = self.page_size * (page - 1)
        q = "SELECT id, meta FROM blog_article" \
            " WHERE pubdate_utc >= :d AND pubdate_utc < date(:d, '+1 month')" \
            " ORDER BY pubdate_utc DESC" \
            " LIMIT :lim OFFSET :off"
        d = datetime.date(year, month, 1)
        cur = self.dbh.cursor()
        cur.execute(q, {'d': d, 'lim': self.page_size, 'off': offset})
        return cur.fetchall()

    def get_day_page(self, year, month, day, page):
        """
        Lists articles in given year and month and day.

        Details see :meth:`get_index_page`.
        """
        if page < 1:
            page = 1
        offset = self.page_size * (page - 1)
        q = "SELECT id, meta FROM blog_article" \
            " WHERE pubdate_utc >= :d AND pubdate_utc < date(:d, '+1 day')" \
            " ORDER BY pubdate_utc DESC" \
            " LIMIT :lim OFFSET :off"
        d = datetime.date(year, month, day)
        cur = self.dbh.cursor()
        cur.execute(q, {'d': d, 'lim': self.page_size, 'off': offset})
        return cur.fetchall()

    def get_author_page(self, author, page):
        """
        Lists articles of given author.

        Details see :meth:`get_index_page`.
        """
        if page < 1:
            page = 1
        offset = self.page_size * (page - 1)
        q = "SELECT id, meta FROM blog_article WHERE author=?" \
            " ORDER BY pubdate_utc DESC" \
            " LIMIT ? OFFSET ?"
        cur = self.dbh.cursor()
        cur.execute(q, (author, self.page_size, offset))
        return cur.fetchall()

    def get_category_page(self, category, page):
        """
        Lists articles with given category.

        Details see :meth:`get_index_page`.
        """
        if page < 1:
            page = 1
        offset = self.page_size * (page - 1)
        q = "SELECT id, meta FROM blog_article WHERE category=?" \
            " ORDER BY pubdate_utc DESC" \
            " LIMIT ? OFFSET ?"
        cur = self.dbh.cursor()
        cur.execute(q, (category, self.page_size, offset))
        return cur.fetchall()

    def get_tag_page(self, tag, page):
        """
        Lists articles with given tag.

        Details see :meth:`get_index_page`.
        """
        if page < 1:
            page = 1
        offset = self.page_size * (page - 1)
        q = "SELECT a.id, a.meta FROM blog_article a" \
            " INNER JOIN blog_article2tag a2t ON a.id=a2t.article_id" \
            " INNER JOIN blog_tag t ON a2t.tag_id=t.id" \
            " WHERE tag=?" \
            " ORDER BY pubdate_utc DESC" \
            " LIMIT ? OFFSET ?"
        cur = self.dbh.cursor()
        cur.execute(q, (tag, self.page_size, offset))
        return cur.fetchall()

    def get_archive_page(self, page):
        """
        Returns archive list.

        An archive list contains only columns ``id``, ``pubdate_utc``,
        ``title`` and ``author``.
        """
        if page < 1:
            page = 1
        offset = self.page_size * (page - 1)
        q = "SELECT id, pubdate_utc, title, author FROM blog_article" \
            " ORDER BY pubdate_utc DESC, title ASC" \
            " LIMIT ? OFFSET ?"
        cur = self.dbh.cursor()
        cur.execute(q, (self.page_size, offset))
        return cur.fetchall()

    def list_authors(self):
        """
        Returns list of authors (author, num articles).
        """
        q = "SELECT author, count(author) FROM blog_article" \
            " GROUP BY author ORDER BY author ASC"
        cur = self.dbh.cursor()
        cur.execute(q)
        return cur.fetchall()

    def list_categories(self):
        """
        Returns list of categories (category, num articles).
        """
        q = "SELECT category, count(category) FROM blog_article" \
            " GROUP BY category ORDER BY category ASC"
        cur = self.dbh.cursor()
        cur.execute(q)
        return cur.fetchall()

    def list_tags(self):
        """
        Returns list of tags (tag, num articles).
        """
        q = "SELECT t.tag, count(t.tag) FROM blog_tag t" \
            " INNER JOIN blog_article2tag a2t ON a2t.tag_id=t.id" \
            " GROUP BY t.tag ORDER BY t.tag ASC"
        cur = self.dbh.cursor()
        cur.execute(q)
        return cur.fetchall()

    def count_articles_per_day(self, year, month):
        """
        Counts articles that were published on a single day.
        Performs this for all days in a given month.
        """
        q = "SELECT date(pubdate_utc), count(*) FROM blog_article" \
            " WHERE pubdate_utc >= :d and pubdate_utc < date(:d, '+1 month')" \
            " GROUP BY date(pubdate_utc) ORDER BY date(pubdate_utc) ASC"
        d = datetime.date(year, month, 1)
        cur = self.dbh.cursor()
        cur.execute(q, {'d': d})
        return cur.fetchall()

    def add_all(self, data):
        """
        Caches the complete data in one transaction.

        Caller must clear the cache with :meth:`clear`, and afterwards
        build the indexes with :meth:`create_indexes`.
        """
        mff = ['relfn', 'slug', 'pubdate_utc', 'title', 'author', 'category']
        q = """INSERT INTO blog_article (id, {0}, meta, summary, body,
            cache_time) VALUES (NULL, {1}, :meta, :summary, :body,
            :cache_time)""".format(','.join(mff), ','.join([':' + f
            for f in mff]))

        def p_gen():
            for it in data:
                d = {f: it[1][f] for f in mff}
                d['meta'] = PickledDict(it[1])
                d['summary'] = it[1]['summary']
                d['body'] = it[0]
                d['cache_time'] = datetime.datetime.now()
                yield d

        cur = self.dbh.cursor()
        try:
            cur.executemany(q, p_gen())
            # Bulk-fetching article IDs like this is only valid if
            # no other records are present. We assume here that the
            # sequence of the newly created IDs matches the sequence
            # of the articles we inserted above.
            q = "SELECT id FROM blog_article ORDER BY id ASC"
            cur.execute(q)
            article_ids = [x[0] for x in cur.fetchall()]
            # Cache the tag ids locally. It is unlikely we get called twice
            # during the lifetime of this cache instance.
            tags = {}
            for i in range(len(data)):
                for t in data[i][1]['tags']:
                    tid = tags.get(t, None)
                    if not tid:
                        cur.execute("INSERT INTO blog_tag (id, tag)"
                            " VALUES(NULL, ?)", (t, ))
                        tid = cur.lastrowid
                    cur.execute("INSERT INTO blog_article2tag"
                        " (article_id, tag_id) VALUES (?, ?)",
                        (article_ids[i], tid))
                    tags[t] = tid
            self.dbh.commit()
        except sqlite3.Error:
            self.dbh.rollback()
            raise

    def add(self, article, meta):
        """
        Adds a single article.

        :returns: Article ID
        """
        mff = ['relfn', 'slug', 'pubdate_utc', 'title', 'author', 'category']
        q = """INSERT INTO blog_article (id, {0}, meta, summary, body,
            cache_time) VALUES (NULL, {1}, :meta, :summary, :body,
            :cache_time)""".format(','.join(mff), ','.join([':' + f
            for f in mff]))
        d = {f: meta[f] for f in mff}
        d['meta'] = PickledDict(meta)
        d['summary'] = meta['summary']
        d['body'] = article
        d['cache_time'] = datetime.datetime.now()
        cur = self.dbh.cursor()
        cur.execute(q, d)
        article_id = cur.lastrowid
        for t in meta['tags']:
            # Cache the tag ids in instance. We may get called multiple
            # times during the lifetime of this cache instance.
            tid = self._tags.get(t, None)
            if not tid:
                try:
                    cur.execute("INSERT INTO blog_tag (id, tag)"
                        " VALUES(NULL, ?)", (t, ))
                    tid = cur.lastrowid
                except sqlite3.IntegrityError:
                    cur.execute("SELECT id FROM blog_tag WHERE tag=?",
                        (t, ))
                    tid = cur.fetchone()[0]
                    self._tags[t] = tid
            cur.execute("INSERT INTO blog_article2tag"
                " (article_id, tag_id) VALUES (?, ?)",
                (article_id, tid))
        self.dbh.commit()
        return article_id

    def update(self, article, meta):
        """
        Updates an article.

        Update first deletes the article, then adds the fresh one.

        :returns: New article ID
        """
        q = "SELECT id FROM blog_article WHERE relfn=?"
        cur = self.dbh.cursor()
        aid = cur.execute(q, meta['relfn']).fetchone()[0]
        self.delete([(aid, )])
        return self.add(article, meta)

    def delete(self, ids):
        """
        Deletes articles by given list of IDs.

        We use ``executemany()``, therefore the IDs must be a list
        of 1-tuples.

        :param ids: List of 1-tuples containing the ID
        """
        cur = self.dbh.cursor()
        # Remove article
        q = "DELETE FROM blog_article WHERE id=?"
        cur.executemany(q, ids)
        # Not sure if foreign key constraint cascades the delete
        q = "DELETE FROM blog_article2tag WHERE article_id=?"
        cur.executemany(q, ids)
        # Remove orphaned tags
        q = "DELETE FROM blog_tag WHERE" \
            " (SELECT count(*) FROM blog_article2tag a2t" \
            "  WHERE a2t.tag_id = blog_tag.id) = 0"
        cur.execute(q)

    def clear(self):
        """
        Clears and vacuums the cache.
        """
        self._tags = {}
        tt = [
            'blog_article',
            'blog_tag',
            'blog_article2tag'
        ]
        with self.dbh:
            for t in tt:
                self.dbh.execute('DROP TABLE ' + t)
            self.dbh.execute('VACUUM')
        self.create_tables()

    def create_tables(self):
        qq = [
            """CREATE TABLE blog_article (
                   id INTEGER PRIMARY KEY
                   , relfn TEXT
                   , slug TEXT
                   , pubdate_utc TIMESTAMP
                   , title TEXT
                   , category TEXT
                   , author TEXT
                   , meta PickledDict
                   , summary TEXT
                   , body TEXT
                   , cache_time TIMESTAMP
               )""",
            """CREATE TABLE blog_tag (
                   id INTEGER PRIMARY KEY
                   , tag TEXT
               )""",
            """CREATE TABLE blog_article2tag (
                   article_id INTEGER
                   , tag_id INTEGER
                   , FOREIGN KEY (article_id) REFERENCES blog_article(id)
                   , FOREIGN KEY (tag_id) REFERENCES blog_tag(id)
               )"""
        ]
        with self.dbh:
            for q in qq:
                self.dbh.execute(q)

    def create_indexes(self):
        ixx = [
            ('blog_article_relfn_ux',       'blog_article', ('relfn', )),
            ('blog_article_slug_ux',        'blog_article', ('slug', )),
            ('blog_article_pubdate_utc_ix', 'blog_article', ('pubdate_utc', )),
            ('blog_article_category',       'blog_article', ('category', )),
            ('blog_article_author',         'blog_article', ('author', )),
            ('blog_article2tag_article_id', 'blog_article2tag',
                ('article_id', )),
            ('blog_article2tag_tag_id',     'blog_article2tag', ('tag_id', )),
            ('blog_tag_tag_ux',             'blog_tag', ('tag', )),
        ]
        tpl = "CREATE {ux}INDEX {name} ON {tbl} ({flds})"
        with self.dbh:
            for ix in ixx:
                ux = 'UNIQUE ' if ix[0].endswith('ux') else ''
                q = tpl.format(ux=ux, name=ix[0], tbl=ix[1],
                    flds=','.join(ix[2]))
                self.dbh.execute(q)

    @property
    def page_size(self):
        return self.rc.get('page_size', 10)

    @page_size.setter
    def page_size(self, v):
        self.rc['page_size'] = v
