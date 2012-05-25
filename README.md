Simple Multiblog
================
Simple Multiblog builds upon the awesome blog, [Simple](https://github.com/orf/simple), and 
adds multiple author functionality.  We loved the simplicity in UI/UX but gave up some of the 
architectural simplicity for some additional features.  However, we think the code base is still pretty easy to follow.  
Props go to [Simple](https://github.com/orf/simple), [Obtvse](https://github.com/NateW/obtvse), 
and [Dustin Curtis' Svbtle](http://dcurt.is/codename-svbtle) for an awesome chain of inspiration.

Simple Multiblog is maintained by [Ryan Macy](https://github.com/rmacy) and [Eric Haughee](https://github.com/ehaughee) 
under the name of [bitrot](https://github.com/bitrot).

####Short list of feature additions
* UI and backend support for multiple authors
* [Gravatar](http://gravatar.com) integration
* [Disqus](http://http://disqus.com/) integration
* Logout functionality (WIP; Simple and Simple-MB use basic auth making logout dicey but auth simple)
* Data model for Authors (users) in addition to Posts


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