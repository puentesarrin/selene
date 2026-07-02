======
Selene
======

A simple CMS for blogging inspired by my beautiful wife and built with Tornado
and MongoDB.

.. important::

   Selene targets Python 3.11+, Tornado 6, and the async PyMongo driver.

Current status
--------------

* No live demo site is maintained.
* Contributors are listed in `CONTRIBUTORS.rst <CONTRIBUTORS.rst>`_.

Requirements
------------

* `Tornado`_
* `PyMongo`_
* `bcrypt`_
* `WTForms`_
* `python-slugify`_
* `aiosmtplib`_

Optional modules
----------------

* `docutils`_ - only needed if you want reStructuredText rendering enabled.
* `Mistune`_ - only needed if you want Markdown rendering enabled.
* `bbcode`_ - only needed if you want BBCode rendering enabled.
* `Textile`_ - only needed if you want Textile rendering enabled.
* `python-creole`_ - only needed if you want Creole rendering enabled.
* `tornado_pyuv`_ - optional libuv IOLoop integration.
* `MongoLog`_ - optional MongoDB-backed logging handler.

Core features
-------------

* Responsive UI with Twitter-Bootstrap.
* Customizable theming.
* Text types for posting:
   * Text plain
   * HTML
   * Markdown
   * reStructuredText
   * BBCode
   * Textile
   * MediaWiki
   * Creole
* Posts sharing via Twitter and Facebook.
* Optional comments management via Disqus.
* Supported localization:
   * Arabic (ar_AR)
   * German (de_DE)
   * English (en_US)
   * Spanish (es_ES)
   * French (fr_FR)
   * Italian (it_IT)
   * Japanese (ja_JP)
   * Macedonian (mk_MK)
   * Brazilian Portuguese (pt_BR)
   * Chinese Simplified (zh_CN)
   * Chinese Traditional (zh_HK, zh_TW)
* Support for Google Analytics and Gravatar.
* Customizable search for publications using regular expressions or full text
  search.

Quickstart
----------

1. Create and activate a virtual environment.
2. Install the project using pip_::

      pip install .

   Install the optional text-format extras you need, for example::

      pip install '[md,rst,bbcode,textile,creole]'

   SMTP is disabled by default; set ``smtp_enabled = True`` in ``selene.conf``
   when you want confirmation and password-reset emails to be sent.

   If you change the server ``port``, update ``base_url`` to match so links
   generated in emails and feeds keep pointing at the running instance.

3. Configure your Selene instance using the ``configure.py`` script.

   The wizard writes ``selene_sample.conf`` and can also bootstrap the
   database with the initial site settings and admin user::

      python configure.py

4. Run your Selene instance::

      python server.py

Administration
--------------

* Admins manage posts and site settings from ``/admin``.
* Comments are created from post pages, and edit/delete is limited to the
  comment author or an admin.

Testing
-------

Run the test suite with::

   python -m unittest discover -s test -v


.. _Tornado: http://www.tornadoweb.org/
.. _PyMongo: http://api.mongodb.org/python/current/
.. _bcrypt: https://pypi.org/project/bcrypt/
.. _docutils: http://sourceforge.net/projects/docutils/
.. _Mistune: https://mistune.lepture.com/
.. _bbcode: https://pypi.org/project/bbcode/
.. _Textile: https://pypi.python.org/pypi/textile
.. _python-creole: https://github.com/jedie/python-creole
.. _WTForms: http://wtforms.simplecodes.com/
.. _pip: http://www.pip-installer.org/en/latest/
.. _tornado_pyuv: https://github.com/saghul/tornado-pyuv
.. _MongoLog: https://pypi.python.org/pypi/mongolog
.. _python-slugify: https://pypi.org/project/python-slugify/
.. _aiosmtplib: https://aiosmtplib.readthedocs.io/en/latest/
