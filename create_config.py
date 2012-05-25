from werkzeug.security import generate_password_hash
from traceback import format_exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import hashlib
import datetime
import os

unapproved_user_names = ['admin', 'Admin', 'new', 'New', 'edit', 'Edit', 'delete', 'Delete', 'preview', 'Preview', 'save', 'Save', 'logout', 'Logout']

def input_with_default(prompt, default):
    x = raw_input("%s (Default %s) "%(prompt, default))
    if not x:
        return default
    return x

def make_gravatar(email):
    url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
    return url

def gen_secret():
    secret = hashlib.sha256(os.urandom(256) + datetime.now().isoformat()).hexdigest()[:32]
    return secret

print "Generating a Simple config file. Please answer some questions:"

with open("settings.py", "w") as fd:
    fd.write("# -*- coding: utf-8 -*-\n\n")

    fd.write("POSTS_PER_PAGE = %s\n"%input_with_default("Posts per page", 5))

    fd.write("ANALYTICS_ID = '%s'\n"%input_with_default("Analytics ID",""))

    fd.write("DISQUS_SHORTNAME = '%s'\n"%input_with_default("Disqus Shortname",""))

    db_uri = input_with_default("Database URI","sqlite:///simple.db")

    fd.write("BACKEND = '%s'\n"%(db_uri))

    admin_username = input_with_default("Admin username","webguy")

    while admin_username in unapproved_user_names:
        print "That username is disallowed!"
        admin_username = input_with_default("Admin username", "webguy")

    admin_password = generate_password_hash(input_with_default("Admin password","password"))

    admin_email = input_with_default("Contact Email", "")

    admin_gravatar = make_gravatar(admin_email)

    admin_github = input_with_default("Github Username", "")

    fd.write("BLOG_NAME = '%s'\n"%input_with_default("Blog Name","Simple-MultiBlog"))

    fd.write("BLOG_URL = '%s'\n"%input_with_default("Blog URL (Please do not include the trailing slash!)",""))

    fd.write("SECRET_KEY = '%s'\n"%gen_secret())

    fd.flush()

import model
Engine = create_engine(db_uri)
Session = sessionmaker(bind=Engine)
session = Session()
try:
    model.Base.metadata.create_all(Engine)
    params = {'username': admin_username, 'password': admin_password, 'github': admin_github, 'email': admin_email, 'gravatar': admin_gravatar}
    user = model.Author(**params)
    session.add(user)
    session.commit()
except:
    print format_exc()
finally:
    session.close()

print "Created!"