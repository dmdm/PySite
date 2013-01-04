# -*- coding: utf-8 -*-

import os
import datetime
import copy
from concurrent import futures
import functools
import dateutil.parser

from pysite.textconv import Markdown
from pysite.exc import PySiteError
import pysite.lib
from pysite.sitemgr.cache import Cache


class Blog(object):

    def __init__(self, cache, rc):
        self.cache = cache
        self.rc = copy.deepcopy(DEFAULT_RC)
        self.rc.update(rc)
        self.errors = None
        self.done = None

        self._content_dir = os.path.abspath(os.path.join(
            self.rc['site_dir'], self.rc['content_dir']))
        self._cache_dir = os.path.join(
            self.rc['site_dir'], 'cache', 'blog')
        for d in [self._content_dir, self._cache_dir]:
            if len(d) < 4:
                raise PySiteError("Invalid directory: '{0}'".format(d))
            if not os.path.exists(d):
                os.makedirs(d)

        self._contentfiles = None

    def build(self, full=False):
        """
        Builds the blog.
        """

        if full:
            self.cache.clear()
        self._collect_content_files()
        proposed = {it['relfn']: it['mtime'] for it in self._contentfiles.values()}
        to_add = self.cache.prepare(proposed, dry_run=False)
        _ = {k: v for k, v in self._contentfiles.items() if v['relfn'] in to_add}
        self._contentfiles = _

        self.errors = []
        self.done = 0
        self._data = []
        if self.rc['max_workers'] < 2:
            self._build_files()
        else:
            self._build_files_parallel()
        if full:
            self.cache.add_all(self._data)
            self.cache.create_indexes()
        else:
            for it in self._data:
                self.cache.add(it[0], it[1])

    def _build_files_parallel(self):
        self._jobs = {}
        f_md = functools.partial(_build_markdown, rc=self.rc['convert'])
        with futures.ProcessPoolExecutor(
                max_workers=self.rc['max_workers']) as executor:
            for fn, it in self._contentfiles.items():
                if it['fmt'] == 'md':
                    # It seems the job function must be a regular function,
                    # cannot be a method.
                    # Else: _pickle.PicklingError: Can't pickle <class
                    #       'method'>: attribute lookup builtins.method failed
                    job = executor.submit(f_md, fn)
                    job.add_done_callback(self._build_file_done)
                    self._jobs[job] = fn
                else:
                    raise PySiteError(
                        "Unknown format '{0}' for file '{1}'".format(
                            it['fmt'], it['relfn']))
        self._jobs = None  # All jobs done

    def _build_file_done(self, job):
        fn = self._jobs[job]
        output, meta, error = job.result()
        self._process_article(fn, output, meta, error)

    def _build_files(self):
        for fn, it in self._contentfiles.items():
            if it['fmt'] == 'md':
                output, meta, error = _build_markdown(fn, rc=self.rc)
            else:
                raise PySiteError(
                    "Unknown format '{0}' for file '{1}'".format(
                        it['fmt'], it['relfn']))
            self._process_article(fn, output, meta, error)

    def _process_article(self, fn, output, meta, error):
        if error:
            self.errors.append({
                'file': fn,
                'error': str(error)
            })
        else:
            # Publication date
            if 'pubdate' in meta:
                meta['pubdate'] = dateutil.parser.parse(meta['pubdate'])
            elif 'date' in meta:
                if isinstance(meta['date'], str):
                    meta['pubdate'] = dateutil.parser.parse(meta['date'])
                else:
                    meta['pubdate'] = meta['date']
            elif 'default_pubdate' in self.rc:
                meta['pubdate'] = dateutil.parser.parse(
                    self.rc['default_pubdate'])
            else:
                meta['pubdate'] = self._contentfiles[fn]['mtime']
            # TODO  Transform pubdate into UTC
            meta['pubdate_utc'] = meta['pubdate']
            # Title, defaults to file name
            if not 'title' in meta or not len(meta['title']):
                meta['title'] = os.path.splitext(os.path.basename(fn))[0]
            if not 'category' in meta or not len(meta['category']):
                meta['category'] = self.rc['default_category']
            if not 'tags' in meta or not len(meta['tags']):
                meta['tags'] = self.rc['default_tags']
            meta['tags'].sort()
            if not 'author' in meta or not len(meta['author']):
                meta['author'] = self.rc['default_author']
            meta['summary'] = pysite.lib.truncate_html_words(output,
                self.rc['summary_max_length'], '&hellip;')
            meta['relfn'] = self._contentfiles[fn]['relfn']
            if not 'slug' in meta or not len(meta['slug']):
                meta['slug'] = os.path.splitext(meta['relfn'])[0].replace(
                    os.path.sep, '^')
            self._data.append((output, meta, ))
            self.done += 1

    def _collect_content_files(self):
        """
        Collect filenames of content files.
        """
        ff = {}
        l = len(self._content_dir)
        for root, dirs, files in os.walk(self._content_dir):
            for f in files:
                if f.startswith('.'):
                    continue
                fmt = os.path.splitext(f)[1].lower()[1:]
                if not fmt in self.rc['allowed_formats']:
                    continue
                fn = os.path.abspath(os.path.join(root, f))
                st = os.stat(fn)
                relfn = fn[l:].lstrip(os.path.sep)
                ff[fn] = dict(
                    relfn=relfn,
                    fmt=fmt,
                    size=st.st_size,
                    mtime=datetime.datetime.fromtimestamp(st.st_mtime)
                )
        self._contentfiles = ff


def _build_markdown(fn, rc):
    c = Markdown(rc)
    c.convert(fn)
    return (c.output, c.meta, c.error)


DEFAULT_RC = {
    # Directory where the content files (articles) are stored.
    # Relative to SITE_ROOT.
    # This is also the slug for the blog in the URL.
    # E.g. content_dir 'blog' has URL 'http://www.example.com/blog'.
    'content_dir': 'blog',
    # List of allowed formats. These denote markup files we know to parse.
    'allowed_formats': ['md'],
    # Max parallel workers for parallel execution
    'max_workers': 1,
    # Options for Converter
    'convert': {
        'typogrify': False,
        'markdown': {}
    },
    # Default publication date for articles that do not define their own date.
    # Comment this out if you want to use the file's modification date.
    # 'default_pubdate': '2013-01-02 11:59'
    # Default category.
    'default_category': 'misc',
    # Default tags. Empty list if you do not want defaults.
    'default_tags': [],
    # Default author
    'default_author': 'Daniel Düsentrieb',
    'summary_max_length': 100
}


if __name__ == '__main__':
    from pprint import pprint

    rc = {
        'site_dir': "/home/dm/myprojects/Pyramid-1.3--Py3.2--env/"
                    "PySite/var/site-templates/default"
    }
    dsn = ':memory:'
    dsn = os.path.join(rc['site_dir'], 'cache', 'blog', 'cache.sqlite3')
    cache = Cache(dsn, {})
    blog = Blog(cache, rc)

    import timeit
    #cache.create_tables()
    t = timeit.timeit('blog.build(full=True)', number=1,
       setup="from __main__ import blog")
    if blog.errors:
        print('****', len(blog.errors), 'ERRORS ****', "\n", blog.errors)
    print('++++', blog.done, 'DONE')
    print('Execution time:', t)

    #data = cache.get_index_page(1)
    #data = cache.list_authors()
    #data = cache.list_categories()
    #data = cache.list_tags()
    #data = cache.count_articles_per_day(1978, 5)
    #data = cache.get_archive_page(1)
    #data = cache.get_author_page('Leila Abouzeid', 1)
    #data = cache.get_category_page('넓은', 1)
    #data = cache.get_tag_page('Gebrauch', 1)
    #data = cache.get_year_page(1968, 1)
    #data = cache.get_month_page(1992, 8, 1)
    #data = cache.get_day_page(2009, 3, 2, 1)
    #data = cache.count_articles()
    #data = cache.get_article_by_id(222)
    #data = cache.get_article_by_relfn('z_zumonawv_index.md')
    #data = cache.get_article_by_slugparts(['btgo1980anl6bek_2010'])
    #pprint(data)
