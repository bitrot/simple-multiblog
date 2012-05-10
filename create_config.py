from werkzeug.security import generate_password_hash
from flaskext.sqlalchemy import SQLAlchemy

def input_with_default(prompt, default):
    x = raw_input("%s (Default %s) "%(prompt, default))
    if not x:
        return default
    return x

print "Generating a Simple config file. Please answer some questions:"

with open("settings.py", "w") as fd:
    fd.write("# -*- coding: utf-8 -*-\n\n")
    fd.write("POSTS_PER_PAGE = %s\n"%input_with_default("Posts per page", 5))
#    fd.write("ADMIN_USERNAME = '%s'\n"%input_with_default("Admin username","admin"))
#    fd.write("ADMIN_PASSWORD = '%s'\n"%generate_password_hash(input_with_default("Admin password","password")) )
    fd.write("ANALYTICS_ID = '%s'\n"%input_with_default("Google analytics ID",""))
    sqlalchemy_uri = input_with_default("Database URI","sqlite:///simple.db")
    fd.write('SQLALCHEMY_DATABASE_URI = "%s"\n'%sqlalchemy_uri)
#    fd.write("GITHUB_USERNAME = '%s'\n"%input_with_default("Github Username", ""))
#    fd.write("CONTACT_EMAIL = '%s'\n"%input_with_default("Contact Email", ""))
    fd.write("BLOG_TITLE = '%s'\n"%input_with_default("Blog title", ""))
    fd.write("BLOG_TAGLINE = '%s'\n"%input_with_default("Blog tagline", ""))
    fd.write("BLOG_URL = '%s'\n"%input_with_default("Blog URL",""))
    fd.flush()

import model
db = SQLAlchemy(sqlalchemy_uri)

username = input_with_default("Admin username","admin")
password = generate_password_hash(input_with_default("Admin password","password"))
github   = input_with_default("Github Username", "")
email    = input_with_default("Contact Email", "")

db.session.add(user)
db.session.commit()

print "Created!"

raw_input()