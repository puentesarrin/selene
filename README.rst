======
Selene
======

A simple CMS for blogging inspired by my beautiful wife and built with Tornado
and MongoDB.

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
* TornadoMail_

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
* Posts sharing via Google+, Twitter and Facebook.
* Optional comments management via Disqus.
* Supported localization:
   * English (en_US)
   * Spanish (es_ES)
   * French (fr_FR)
   * Japanese (ja_JP)
   * Chinese Simplified (zh_CN)
   * Chinese Traditional (zh_HK, zh_TW)
* Support for Google Analytics and Gravatar.
* Customizable search for publications using regular expressions or full text
  search.

Contributors
------------

* Lowstz Chen (`@lowstz <https://github.com/lowstz>`_)
* Juan Carlos Farah (`@juancarlosfarah <https://github.com/juancarlosfarah>`_)
* Luigi Van (`@fdb713 <https://github.com/fdb713>`_)

I want to improve this project with your help... I will watch to all of your
pull-requests!

.. _Tornado: http://www.tornadoweb.org/
.. _PyMongo: http://api.mongodb.org/python/current/
.. _Motor: https://motor.readthedocs.org/en/latest/
.. _py-bcrypt: https://code.google.com/p/py-bcrypt/
.. _docutils: http://sourceforge.net/projects/docutils/
.. _Misaka: https://github.com/FSX/misaka
.. _Postmarkup: https://code.google.com/p/postmarkup/
.. _Textile: https://pypi.python.org/pypi/textile
.. _WTForms: http://wtforms.simplecodes.com/
.. _TornadoMail: https://github.com/equeny/tornadomail
