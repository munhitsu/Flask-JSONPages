# coding: utf8
"""
    flask_jsonpages.jsonpages
    ~~~~~~~~~~~~~~~~~~

    Flask-JSONPages provides a collections of pages to your Flask application.
    Pages are built from JSON files as opposed to a relational database.
    It is based on Flask-FlaskPages by Simon Sapin that used yaml as format.

    :copyright: (c) 2012 by Mateusz Łapsa-Malawski.
    :license: BSD, see LICENSE for more details.
"""

import os.path

import werkzeug
import flask
import json


class JSONPage(object):
    def __init__(self, path, content_json_str):
        """
        Initialize JSONPage object based on path and content_str.
        Expects that content_json_str is a json dictionary.
        """
        #: Path this pages was obtained from, as in ``pages.get(path)``.
        self.path = path
        #: Content of the pages.
        self.content_json_str = content_json_str

    def __repr__(self):
        return '<JSONPage %r>' % self.path

    @werkzeug.cached_property
    def content(self):
        """
        Performs translation of content_json_str into json object.
        Expects that content_json_str is a json dictionary.
        """
        content = json.loads(self.content_json_str)
        if not content:
            return {}
        assert isinstance(content, dict)
        return content

    def __getitem__(self, name):
        """Shortcut for accessing content dictionary.

        ``page['title']`` or, in a template, ``{{ page.title }}`` are
        equivalent to ``page.content['title']``.
        """
        return self.content[name]


class JSONPages(object):
    """
    A proxy to all 'JSONPage's

    :param app: your application
    :type app: Flask instance
    """
    def __init__(self, app):
        app.config.setdefault('JSONPAGES_ROOT', 'pages')
        app.config.setdefault('JSONPAGES_EXTENSION', '.json')
        app.config.setdefault('JSONPAGES_ENCODING', 'utf8')
        app.config.setdefault('JSONPAGES_INDEX', 'index')
        self.app = app

        #:dict of filename: (page object, mtime when loaded)
        self._file_cache = {}

    def get(self, url_path):
        """
        :Return: the :class:`JSONPage` object initialized from ``url_path``
        """
        extension = self.app.config['JSONPAGES_EXTENSION']
        index_name = self.app.config['JSONPAGES_INDEX']
        file_path = os.path.join(self.root,url_path)
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path,"%s%s" % (index_name, extension))
        else:
            file_path = "%s%s" % (file_path, extension)
        return self._load_file(url_path, file_path)

    def get_or_404(self, url_path):
        """:Return: the :class:`JSONPage` object at ``url_path``.
        :raises: :class:`NotFound` if the pages does not exist.
                 This is caught by Flask and triggers a 404 error.
        """
        try:
            page = self.get(url_path)
        except OSError:
            flask.abort(404)
        return page

    @werkzeug.cached_property
    def root(self):
        """Full path to the directory where pages are looked for.

        It is the `JSONPAGES_ROOT` config value, interpreted as relative to
        the app root directory.
        """
        return os.path.join(self.app.root_path,
                            self.app.config['JSONPAGES_ROOT'])


    def _load_file(self, path, filename):
        """
        Opens file while caching it's parsed content (compares mtime of file)
        :return: the :class:'JSONPage'
        :raises: :class:`NotFound` if the file was not found
        """
        mtime = os.path.getmtime(filename)
        cached = self._file_cache.get(filename)
        if cached and cached[1] == mtime:
            page = cached[0]
        else:
            with open(filename) as fd:
                content = fd.read().decode(
                    self.app.config['JSONPAGES_ENCODING'])
            page = JSONPage(path, content)
            self._file_cache[filename] = page, mtime
        return page
