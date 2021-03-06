# -*- coding: utf-8 -*-

from sys import exit
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from simple import unapproved_user_names
import hashlib

try:
    import settings
except ImportError:
    exit("Cannot create user without a generated settings file.")

def input_with_default(prompt, default):
    x = raw_input("%s (Default %s) "%(prompt, default))
    if not x:
        return default
    return x

def make_gravatar(email):
    url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
    return url

admin_username = input_with_default("Admin Username","webguy")

while admin_username in unapproved_user_names:
    print "That username is disallowed!"
    admin_username = input_with_default("Admin Username", "webguy")

admin_password = generate_password_hash(input_with_default("Admin Password","password"))

admin_email = input_with_default("Contact Email", "")

while not admin_email:
    print "Please provide an email. This will be used to generate your gravatar image."
    admin_email = input_with_default("Contact Email", "")

admin_gravatar = make_gravatar(admin_email)

admin_github = input_with_default("Github Username", "")

admin_linkedin = input_with_default("LinkedIn URL, (http://www.linkedin.com/in/ryanmacy; the ryanmacy portion)", "")

admin_stackoverflow = input_with_default("Stack Overflow ID (www.stackoverflow.com/users/{id}", "")

import model
Engine = create_engine(settings.BACKEND)
Session = sessionmaker(bind=Engine)
session = Session()

try:
    params = {'username': admin_username, 'password': admin_password, 'github': admin_github, 'linkedin': admin_linkedin, 'stackoverflow': admin_stackoverflow, 'email': admin_email, 'gravatar': admin_gravatar}
    user = model.Author(**params)
    session.add(user)
    session.commit()
except IntegrityError as e:
    exit('That user already seems to exist!')
finally:
    session.close()

print "Created!"