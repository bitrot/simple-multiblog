from werkzeug.security import generate_password_hash
from traceback import format_exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    import settings
except ImportError:
    print "You need to create the settings file before you can add more users!"

def input_with_default(prompt, default):
    x = raw_input("%s (Default %s) "%(prompt, default))
    if not x:
        return default
    return x

admin_username = input_with_default("Admin username","admin")
admin_password = generate_password_hash(input_with_default("Admin password","password"))
admin_email = input_with_default("Contact Email", "")
admin_github = input_with_default("Github Username", "")

import model
Engine = create_engine(settings.BACKEND)
Session = sessionmaker(bind=Engine)
session = Session()
try:
    params = {'username': admin_username, 'password': admin_password, 'github': admin_github, 'email': admin_email}
    user = model.User(**params)
    session.add(user)
    session.commit()
except:
    print format_exc()
finally:
    session.close()

print "Created!"