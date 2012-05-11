from werkzeug.security import generate_password_hash
from traceback import format_exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def input_with_default(prompt, default):
    x = raw_input("%s (Default %s) "%(prompt, default))
    if not x:
        return default
    return x

print "Generating a Simple config file. Please answer some questions:"

with open("settings.py", "w") as fd:
    fd.write("# -*- coding: utf-8 -*-\n\n")

    fd.write("POSTS_PER_PAGE = %s\n"%input_with_default("Posts per page", 5))

    fd.write("ANALYTICS_ID = '%s'\n"%input_with_default("Google analytics ID",""))

    db_uri = input_with_default("Database URI","sqlite:///simple.db")

    fd.write("BACKEND = '%s'\n"%(db_uri))

    admin_username = input_with_default("Admin username","admin")

    admin_password = generate_password_hash(input_with_default("Admin password","password"))

    admin_email = input_with_default("Contact Email", "")

    admin_github = input_with_default("Github Username", "")

    fd.write("BLOG_TITLE = '%s'\n"%input_with_default("Blog title", ""))

    fd.write("BLOG_TAGLINE = '%s'\n"%input_with_default("Blog tagline", ""))

    fd.write("BLOG_URL = '%s'\n"%input_with_default("Blog URL",""))

    fd.flush()

import model
Engine = create_engine(db_uri)
Session = sessionmaker(bind=Engine)
session = Session()
try:
    model.Base.metadata.create_all(Engine)
    params = {'username': admin_username, 'password': admin_password, 'github': admin_github, 'email': admin_email}
    user = model.User(**params)
    session.add(user)
    session.commit()
except:
    print format_exc()
finally:
    session.close()

print "Created!"

raw_input()