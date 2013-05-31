======
Selene
======

A simple CMS for blogging inspired by my beautiful wife and built with Tornado
and MongoDB. See a demo site `here <http://selene.lowstz.org>`_.

.. important::

   For this project we have considered to move all MongoDB operations from
   PyMongo_ to Motor_, the asynchronous Python driver for Tornado_, any changes
   regarding this can be found in a branch named
   `"motor" <https://github.com/puentesarrin/selene/tree/motor>`_.

Requirements
------------

* Tornado_
* PyMongo_
* py-bcrypt_
* WTForms_
* docutils_
* Misaka_
* Postmarkup_
* Textile_
* mediawiki_
* TornadoMail_
* python-creole_
* Werkzeug_

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
* Posts sharing via Google+, Twitter and Facebook.
* Optional comments management via Disqus.
* Supported localization:
   * Arabic (ar_AR)
   * German (de_DE)
   * English (en_US)
   * Spanish (es_ES)
   * French (fr_FR)
   * Japanese (ja_JP)
   * Macedonian (mk_MK)
   * Chinese Simplified (zh_CN)
   * Chinese Traditional (zh_HK, zh_TW)
* Support for Google Analytics and Gravatar.
* Customizable search for publications using regular expressions or full text
  search.

Installing and Running
----------------------

1. Install the requirements using pip_::

      pip install -r requirements.txt

#. Configure your Selene instance using the ``configure.py`` script, setting
   all available options::

      python configure.py

#. Run your Selene instance::

      python server.py

Contributors
------------

* Elena Petrevska (`@el3na77 <https://twitter.com/el3na77>`_ in Twitter)
* Samar Hazboun (`@Samar_Hazboun <https://twitter.com/Samar_Hazboun>`_ in Twitter)
* Lowstz Chen (`@lowstz <https://github.com/lowstz>`_)
* Juan Carlos Farah (`@juancarlosfarah <https://github.com/juancarlosfarah>`_)
* Luigi Van (`@fdb713 <https://github.com/fdb713>`_)
* Liangyi Zhang (`@SidneyZhang <https://twitter.com/SidneyZhang>`_ in Twitter)

I want to improve this project with your help... I'm looking forward for all of
your pullrequests!

.. _Tornado: http://www.tornadoweb.org/
.. _PyMongo: http://api.mongodb.org/python/current/
.. _Motor: https://motor.readthedocs.org/en/latest/
.. _py-bcrypt: https://code.google.com/p/py-bcrypt/
.. _docutils: http://sourceforge.net/projects/docutils/
.. _Misaka: https://github.com/FSX/misaka
.. _Postmarkup: https://code.google.com/p/postmarkup/
.. _Textile: https://pypi.python.org/pypi/textile
.. _mediawiki: https://github.com/zikzakmedia/python-mediawiki
.. _python-creole: https://github.com/jedie/python-creole
.. _WTForms: http://wtforms.simplecodes.com/
.. _TornadoMail: https://github.com/equeny/tornadomail
.. _pip: http://www.pip-installer.org/en/latest/
.. _Werkzeug: http://werkzeug.pocoo.org/