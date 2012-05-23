from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Sequence, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
import json
import markdown

Base = declarative_base()

class Author(Base):
    __tablename__ = "authors"

    id           = Column(Integer(11), Sequence('author_id_sequence'), primary_key = True, nullable = False)
    username     = Column(String(255), unique = True, index = True, nullable = False)
    password     = Column(String(255), nullable = False)
    email        = Column(String(255), nullable = False)
    github       = Column(String(255))
    bio          = Column(Text)
    post         = relationship('Post', backref='author')
    created_at   = Column(DateTime, default=datetime.datetime.utcnow(), index = True, nullable = False)
    updated_at   = Column(DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow(), nullable = False)

    def __init__(self, *args, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __unicode__(self):
        return "%s %s %s %s" % (self.id, self.username, self.email, self.github)

    public_field = ('id', 'username', 'email', 'github', 'bio', 'created_at')

    def get_public(self):
        data = {}
        for field in self.public_field:
            data[field] = getattr(self, field, '')
        return data

    def get_json(self):
        return json.dumps(self.get_public())

class Post(Base):
    __tablename__ = "posts"

    id           = Column(Integer(11), Sequence('post_id_sequence'), primary_key = True, nullable = False)
    title        = Column(String(255), nullable = False)
    author_id    = Column(ForeignKey(Author.id), nullable = False)
    slug         = Column(String(255), unique = True)
    text         = Column(String(255), default = "")
    draft        = Column(Boolean, index = True)
    views        = Column(Integer(11), default = 0)
    created_at   = Column(DateTime, default=datetime.datetime.utcnow(), index = True, nullable = False)
    updated_at   = Column(DateTime, default=datetime.datetime.utcnow(), onupdate = datetime.datetime.utcnow(), nullable = False)

    def __init__(self, *args, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __unicode__(self):
        return "%s %s %s" % (self.title, self.text, self.created_at)

    public_field = ('id', 'title', 'author', 'slug', 'text', 'draft', 'views', 'created_at', 'updated_at')

    def get_public(self):
        data = {}
        for field in self.public_field:
            data[field] = getattr(self, field, '')
        return data

    def get_json(self):
        return json.dumps(self.get_public())

    def render_content(self):
        return markdown.Markdown(extensions=['fenced_code'], output_format="html5", safe_mode=True).convert(self.text)
