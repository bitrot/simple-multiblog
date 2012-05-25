Simple Multiblog
================
An extension of [Simple](https://github.com/orf/simple) that adds multiple author functionality.

(We really liked Simple, Obtvse, and Svbtle, but wanted multiple authors and a few other features. \- [rmacy](https://github.com/rmacy) and [ehaughee](https://github.com/ehaughee))

About
============
The point of Simple is to be simple. The blog is 1 file (excluding resources) with a few simple pure-python dependancies, it doesn't
require a database server, has a small footprint and is fairly fast.

Installation
============
Its quite simple. Go download Python 2.7+, Flask, Sqlalchemy and flask-sqlalchemy and you are good to go.
To create a settings file run create_config.py and enter some details, then run simple.py.

Deployment
============
Deploying Simple is easy. Simply clone this repo (or your own) and install [Gunicorn](http://gunicorn.org/).
Then cd to the directory containing simple.py and run the following command:
``gunicorn -w 4 simple:app``
This will start 4 gunicorn workers serving Simple. You can then use nginx or apache to forward requests to Gunicorn.

Example
============
You can see the blog live @ [bitrot](http://bitrot.io/).

Screenshots
===========
- - -
![Admin](https://s3.amazonaws.com/bitrot/bitrot_docs_admin.png)
- - -
![Draft](https://s3.amazonaws.com/bitrot/bitrot_docs_edit.png)
- - -
![Live](https://s3.amazonaws.com/bitrot/bitrot_docs_post.png)
- - -
![Author] (https://s3.amazonaws.com/bitrot/bitrot_docs_author_eric.png)
- - -
![Author] (https://s3.amazonaws.com/bitrot/bitrot_docs_author_ryan.png)
- - -
![Authors] (https://s3.amazonaws.com/bitrot/bitrot_docs_multi_user.png)
- - -