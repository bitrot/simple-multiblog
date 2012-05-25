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
First clone the repo:
``git clone git://github.com/bitrot/simple-multiblog.git``

Install [Gunicorn](http://gunicorn.org) with [PIP](https://crate.io/packages/pip/):
``pip install gunicorn``

Descend into the simple-multiblog directory:
``cd simple-multiblog``

Install dependancies:
``pip install -U -r .requirements``

Create the config:
``python create_config.py``

And you're good to go!

(To add users run ``python add_user.py``)

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