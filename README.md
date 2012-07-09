Simple Multiblog
================
Simple Multiblog builds upon the awesome blog, [Simple](https://github.com/orf/simple), and 
adds multiple author functionality.  We loved the simplicity in UI/UX but we traded portions of the
architectural sugar for additional features.  However, we think the code base is still pretty easy to follow.
Props go to [Simple](https://github.com/orf/simple), [Obtvse](https://github.com/NateW/obtvse), 
and [Dustin Curtis' Svbtle](http://dcurt.is/codename-svbtle) for an awesome chain of inspiration.

Simple Multiblog is maintained by [Ryan Macy](https://github.com/rmacy) and [Eric Haughee](https://github.com/ehaughee) 
under the name [bitrot](https://github.com/bitrot).

####Short list of feature additions
* UI and backend support for multiple authors
* [Gravatar](http://gravatar.com) integration
* [Disqus](http://disqus.com/) integration
* Logout functionality (WIP; Simple and Simple-MB use basic auth making logout dicey but in turn authentication simple)
* Data model for Authors (users) in addition to Posts


Installation
============
First clone the repo: ``git clone git://github.com/bitrot/simple-multiblog.git``

Install [Gunicorn](http://gunicorn.org) with [PIP](https://crate.io/packages/pip/): ``pip install gunicorn``

Descend into the simple-multiblog directory: ``cd simple-multiblog``

Install dependancies: ``pip install -U -r .requirement``

Create the config: ``python create_config.py``

And you're good to go!

(To add users run ``python add_user.py``)

Deployment
============

_Quick Note: The -w flag for gunicorn signifies how many processes (read workers) you want to start. The recommended amount of workers is 2x the number of cores per CPU._


####With NGINX

To deploy, install & setup [NGINX](http://nginx.org/). See how to configure NGINX with Gunicorn [here](http://gunicorn.org/deploy.html).

Navigate to your simple-multiblog directory and start some gunicorn processes: ``gunicorn -w 4 -b unix:/tmp/gunicorn.sock simple:app -D``


####Without NGINX

To deploy without NGINX, navigate to the simple-multiblog directory and start some gunicorn processes: ``gunicorn -w 4 -b 0.0.0.0 simple:app -D``

Caveat! gunicorn is very susceptible to denial-of-service attacks without a proxy buffer like NGINX.


####Flask Development Server

Naviagate to your simple-multiblog directory and run: ``python simple.py`` to start the development server.

Open ``simple.py`` with your favorite editor and change ``app.debug = False`` to ``app.debug = True`` to turn on the development features of Flask.

The server will automatically reload when it detects a code change when ``app.debug = True`` is set.

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