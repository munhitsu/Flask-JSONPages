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
    A collections of :class:`Page` objects.

    :param app: your application
    :type app: Flask instance
    """
    def __init__(self, app):
        app.config.setdefault('JSONPAGES_ROOT', 'pages')
        app.config.setdefault('JSONPAGES_EXTENSION', '.json')
        app.config.setdefault('JSONPAGES_ENCODING', 'utf8')
        app.config.setdefault('JSONPAGES_AUTO_RELOAD', True)
        self.app = app

        #: dict of filename: (page object, mtime when loaded)
        self._file_cache = {}

        app.before_request(self._conditional_auto_reset)

    def _conditional_auto_reset(self):
        """Reset if configured to do so on new requests."""
        if self.app.config['JSONPAGES_AUTO_RELOAD'] or self.app.debug:
            self.reload()

    def reload(self):
        """Forget all pages.
        All pages will be reloaded next time they're accessed"""
        try:
            # This will "unshadow" the cached_property.
            # The property will be re-executed on next access.
            del self.__dict__['_pages']
        except KeyError:
            pass

    def __iter__(self):
        """Iterate on all :class:`Page` objects."""
        return self._pages.itervalues()

    def get(self, path, default=None):
        """
        :Return: the :class:`Page` object at ``path``, or ``default``
                 if there is none.
        """
        # This may trigger the property. Do it outside of the try block.
        pages = self._pages
        try:
            return pages[path]
        except KeyError:
            return default

    def get_or_404(self, path):
        """:Return: the :class:`Page` object at ``path``.
        :raises: :class:`NotFound` if the pages does not exist.
                 This is caught by Flask and triggers a 404 error.
        """
        print path
        page = self.get(path)
        if not page:
            flask.abort(404)
        return page

    @property
    def root(self):
        """Full path to the directory where pages are looked for.

        It is the `JSONPAGES_ROOT` config value, interpreted as relative to
        the app root directory.
        """
        return os.path.join(self.app.root_path,
                            self.app.config['JSONPAGES_ROOT'])

    @werkzeug.cached_property
    def _pages(self):
        """Walk the page root directory an return a dict of
        unicode path: page object.
        """
        def _walk(directory, path_prefix=()):
            for name in os.listdir(directory):
                full_name = os.path.join(directory, name)
                if os.path.isdir(full_name):
                    _walk(full_name, path_prefix + (name,))
                elif name.endswith(extension):
                    name_without_extension = name[:-len(extension)]
                    path = u'/'.join(path_prefix + (name_without_extension,))
                    pages[path] = self._load_file(path, full_name)

        extension = self.app.config['JSONPAGES_EXTENSION']
        pages = {}
        _walk(self.root)
        return pages

    def _load_file(self, path, filename):
        mtime = os.path.getmtime(filename)
        cached = self._file_cache.get(filename)
        if cached and cached[1] == mtime:
            # cached == (page, old_mtime)
            page = cached[0]
        else:
            with open(filename) as fd:
                content = fd.read().decode(
                    self.app.config['JSONPAGES_ENCODING'])
            page = JSONPage(path, content)
            self._file_cache[filename] = page, mtime
        return page

