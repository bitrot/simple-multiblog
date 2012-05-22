from sys import exit
from werkzeug.security import generate_password_hash
from traceback import format_exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    import settings
except ImportError:
    exit("You need to create the settings file before you can add more users!")

unapproved_user_names = ['admin', 'Admin', 'new', 'New', 'edit', 'Edit', 'delete', 'Delete', 'preview', 'Preview']

def input_with_default(prompt, default):
    x = raw_input("%s (Default %s) "%(prompt, default))
    if not x:
        return default
    return x

admin_username = input_with_default("Admin username","webguy")

while admin_username in unapproved_user_names:
    print "That username is disallowed!"
    admin_username = input_with_default("Admin username", "webguy")

admin_password = generate_password_hash(input_with_default("Admin password","password"))
admin_email = input_with_default("Contact Email", "")
admin_github = input_with_default("Github Username", "")

import model
Engine = create_engine(settings.BACKEND)
Session = sessionmaker(bind=Engine)
session = Session()
try:
    params = {'username': admin_username, 'password': admin_password, 'github': admin_github, 'email': admin_email}
    try:
        user = model.Author(**params)
        session.add(user)
        session.commit()
    except IntegrityError as e:
        exit('That user already seems to exist!')
except:
    exit(format_exc())
finally:
    session.close()

print "Created!"