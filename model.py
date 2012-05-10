from flaskext.sqlalchemy import SQLAlchemy

# setup SQLAlchemy models
# TODO: use declarative base
class Post(db.Model):
    __tablename__ = "posts"

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String())
    author       = db.Column(db.Sring()) # this should be a FK
    slug         = db.Column(db.String(), unique=True)
    text         = db.Column(db.String(), default="")
    draft        = db.Column(db.Boolean(), index=True, default=True)
    views        = db.Column(db.Integer(), default=0)
    created_at   = db.Column(db.DateTime, default=datetime.datetime.utcnow(), index=True)
    updated_at   = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    def render_content(self):
        return markdown.Markdown(extensions=['fenced_code'], output_format="html5", safe_mode=True).convert(self.text)

class User(db.Model):
    __tablename__ = "users"

    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(), index=True)
    password     = db.Column(db.String())
    email        = db.Column(db.String())
    github       = db.Column(db.String())
    bio          = db.Column(db.Text())
    created_at   = db.Column(db.DateTime, default=datetime.datetime.utcnow(), index=True)
    updated_at   = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    def __unicode__(self):
        return "%s %s" % (self.id, self.username)

# create if not exists -- SQLAlchemy
try:
    db.create_all()
except Exception:
    app.logger.error(format_exc())