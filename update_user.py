# -*- coding: utf-8 -*-

# The goal of this file is to present a list of options in the command line,
# select an option, and then update that option, finally represtening that
# list. The list will have an exit option.

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
    exit('Cannot update the user without a generated settings file.')

