import hashlib
import re
import datetime
import markdown
from werkzeug.security import check_password_hash
from unicodedata import normalize
from flaskext.sqlalchemy import SQLAlchemy
from flaskext.oauth import OAuth
from flask import render_template, request, Flask, flash, redirect, url_for, abort, jsonify, Response as response, make_response
from functools import wraps
from traceback import format_exc

app = Flask(__name__)
app.config.from_object('settings')
db = SQLAlchemy(app)

# TODO: Add error level email handler

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

# setup SQLAlchemy models
# TODO: use declarative base
class Post(db.Model):
    __tablename__ = "posts"

    id    = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    author = db.Column(db.Sring()) # this should be a FK
    slug  = db.Column(db.String(), unique=True)
    text  = db.Column(db.String(), default="")
    draft = db.Column(db.Boolean(), index=True, default=True)
    views = db.Column(db.Integer(), default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow(), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

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

# we are going to replace this probably
def requires_authentication(f):
    @wraps(f)
    def _auth_decorator(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return response("Could not authenticate you", 401, {"WWW-Authenticate":'Basic realm="Login Required"'})
        else:
            try:
                user = db.session.query(User).filter_by(username=auth.username).first()
            except Exception:
                return response("Could not authenticate you", 401, {"WWW-Authenticate":'Basic realm="Login Required"'})

            if not (auth.username == user.username
                    and check_password_hash(user.password, auth.password)):
                return response("Could not authenticate you", 401, {"WWW-Authenticate":'Basic realm="Login Required"'})

        return f(*args, **kwargs)

    return _auth_decorator

@app.route("/")
def index():
    page = request.args.get("page", 0, type=int)
    posts_master = db.session.query(Post).filter_by(draft=False).order_by(Post.created_at.desc())
    posts_count = posts_master.count()

    posts = posts_master.limit(app.config["POSTS_PER_PAGE"]).offset(page*app.config["POSTS_PER_PAGE"]).all()
    is_more = posts_count > ((page*app.config["POSTS_PER_PAGE"]) + app.config["POSTS_PER_PAGE"])

    return render_template("index.html", posts=posts, now=datetime.datetime.now(),
                                         is_more=is_more, current_page=page)

@app.route("/<author>") # all posts by author
def view_post_by_author(author):
    pass

@app.route("/<int:post_id>")
def view_post(post_id):
    try:
        post = db.session.query(Post).filter_by(id=post_id, draft=False).one()
    except Exception:
        return abort(404)

    db.session.query(Post).filter_by(id=post_id).update({Post.views:Post.views+1})
    db.session.commit()

    return render_template("view.html", post=post)

@app.route("/<slug>")
def view_post_slug(slug):
    try:
        post = db.session.query(Post).filter_by(slug=slug,draft=False).one()
    except Exception:
        return abort(404)

    db.session.query(Post).filter_by(slug=slug).update({Post.views:Post.views+1})
    db.session.commit()

    pid = request.args.get("pid", "0")
    return render_template("view.html", post=post, pid=pid)

@app.route("/new", methods=["POST", "GET"])
@requires_authentication
def new_post():
    post = Post()
    post.title = request.form.get("title","untitled")
    post.slug = slugify(post.title)
    post.created_at = datetime.datetime.now()
    post.updated_at = datetime.datetime.now()

    db.session.add(post)
    db.session.commit()

    return redirect(url_for("edit", id=post.id))

@app.route("/edit/<int:id>", methods=["GET","POST"])
@requires_authentication
def edit(id):
    try:
        post = db.session.query(Post).filter_by(id=id).one()
    except Exception:
        return abort(404)

    if request.method == "GET":
        return render_template("edit.html", post=post)
    else:
        if post.title != request.form.get("post_title", ""):
            post.title = request.form.get("post_title","")
            post.slug = slugify(post.title)
        post.text = request.form.get("post_content","")
        post.updated_at = datetime.datetime.now()

        if any(request.form.getlist("post_draft", type=int)):
            post.draft = True
        else:
            post.draft = False

        db.session.add(post)
        db.session.commit()
        return redirect(url_for("edit", id=id))

@app.route("/delete/<int:id>", methods=["GET","POST"])
@requires_authentication
def delete(id):
    try:
        post = db.session.query(Post).filter_by(id=id).one()
    except Exception:
        flash("Error deleting post ID %s"%id, category="error")
    else:
        db.session.delete(post)
        db.session.commit()

    return redirect(request.args.get("next","") or request.referrer or url_for('index'))

@app.route("/admin", methods=["GET", "POST"])
@requires_authentication
def admin():
    drafts = db.session.query(Post).filter_by(draft=True)\
                                          .order_by(Post.created_at.desc()).all()
    posts  = db.session.query(Post).filter_by(draft=False)\
                                          .order_by(Post.created_at.desc()).all()
    return render_template("admin.html", drafts=drafts, posts=posts)

@app.route("/admin/save/<int:id>", methods=["POST"])
@requires_authentication
def save_post(id):
    try:
        post = db.session.query(Post).filter_by(id=id).one()
    except Exception:
        return abort(404)
    if post.title != request.form.get("title", ""):
        post.title = request.form.get("title","")
        post.slug = slugify(post.title)
    post.text = request.form.get("content", "")
    post.updated_at = datetime.datetime.now()
    db.session.add(post)
    db.session.commit()
    return jsonify(success=True)

@app.route("/preview/<int:id>")
@requires_authentication
def preview(id):
    try:
        post = db.session.query(Post).filter_by(id=id).one()
    except Exception:
        return abort(404)

    return render_template("post_preview.html", post=post)

@app.route("/posts.rss")
def feed():
    posts = db.session.query(Post).filter_by(draft=False).order_by(Post.created_at.desc()).limit(10).all()

    r = make_response(render_template('index.xml', posts=posts))
    r.mimetype = "application/xml"
    return r

def slugify(text, delim=u'-'):
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', unicode(word)).encode('ascii', 'ignore')
        if word:
            result.append(word)
    slug = unicode(delim.join(result))
    _c = db.session.query(Post).filter_by(slug=slug).count()
    if _c > 0:
        return "%s%s%s" % (slug, delim, _c)
    else:
        return slug

if __name__ == "__main__":
    app.run()