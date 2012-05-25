import re
import datetime
import urllib
from sys import exit
from werkzeug.security import check_password_hash
from unicodedata import normalize
from model import Post, Author
from flaskext.oauth import OAuth
from flaskext.sqlalchemy import SQLAlchemy
from flask import render_template, session, request, Flask, flash, redirect, url_for, abort, jsonify, Response as response, make_response
from functools import wraps
from traceback import format_exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from settings import BACKEND
    Engine = create_engine(BACKEND)
    Session = sessionmaker(bind=Engine)
    db_session = Session()
except ImportError:
    exit("You need to create the settings file before you can run simple-multiblog!")


#$$$$$$$#
# FLASK #
#$$$$$$$#

app = Flask(__name__)
app.debug = True
app.config.from_object('settings')
app.secret_key = app.config["SECRET_KEY"]


#%%%%%%%#
# UTILS #
#%%%%%%%#

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def requires_authentication(f):
    @wraps(f)
    def _auth_decorator(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return response("Could not authenticate you", 401, {"WWW-Authenticate":'Basic realm="Login Required"'})
        else:
            if auth.username and auth.password:
                try:
                    author = db_session.query(Author).filter_by(username=auth.username).first()
                except Exception:
                    app.logger.debug(format_exc())
                    return response("Could not authenticate you", 401, {"WWW-Authenticate":'Basic realm="Login Required"'})

                if not check_password_hash(author.password, auth.password):
                    return response("Could not authenticate you", 401, {"WWW-Authenticate":'Basic realm="Login Required"'})
            else:
                return response("Could not authenticate you", 401, {"WWW-Authenticate":'Basic realm="Login Required"'})

        session["user_name"] = author.username
        session["user_id"]  = author.id

        
        return f(*args, **kwargs)

    return _auth_decorator

def slugify(text, delim=u'-'):
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', unicode(word)).encode('ascii', 'ignore')
        if word:
            result.append(word)
    slug = unicode(delim.join(result))
    _c = db_session.query(Post).filter_by(slug=slug).count()
    if _c > 0:

        return "%s%s%s" % (slug, delim, _c)
    else:

        return slug

def get_gravatar_url(url, size=80):
    default = 'retro'
    url += urllib.urlencode({'d':default, 's':str(size)})

    return url


#%%%%%%%%#
# ROUTES #
#%%%%%%%%#

@app.route("/", methods=["GET"])
def index():
    page = request.args.get("page", 0, type=int)

    posts_master = db_session.query(Post).filter_by(draft=False).order_by(Post.created_at.desc())
    posts_count = posts_master.count()

    posts = posts_master.limit(app.config["POSTS_PER_PAGE"]).offset(page*app.config["POSTS_PER_PAGE"]).all()
    is_more = posts_count > ((page*app.config["POSTS_PER_PAGE"]) + app.config["POSTS_PER_PAGE"])

    _authors = db_session.query(Author).all()
    authors = []

    for author in _authors:
        if author.gravatar:
            author.gravatar_url = get_gravatar_url(author.gravatar)
        authors.append(author)

    return render_template("index.html", posts=posts, now=datetime.datetime.now(), is_more=is_more, current_page=page, authors=authors)

@app.route("/posts.rss", methods=["GET"])
def feed(author=None):
    try:
        if author:
            posts = db_session.query(Post).join(Author).filter(Author.username==author, Post.draft==False).order_by(Post.created_at.desc()).limit(10).all()
        else:
            posts = db_session.query(Post).filter_by(draft=False).order_by(Post.created_at.desc()).limit(10).all()
    except Exception:
        app.logger.debug(format_exc())
        return abort(404)

    r = make_response(render_template('index.xml', posts=posts))
    r.mimetype = "application/xml"

    return r

@app.route("/<author>", methods=["GET"])
def get_author_posts(author):
    page = request.args.get("page", 0, type=int)

    count = db_session.query(Author).filter_by(username=author).count()

    if count < 1:
        return abort(404)

    posts_master = db_session.query(Post).join(Author).filter(Author.username==author, Post.draft==False).order_by(Post.created_at.desc())
    posts_count = posts_master.count()

    posts = posts_master.limit(app.config["POSTS_PER_PAGE"]).offset(page*app.config["POSTS_PER_PAGE"]).all()
    is_more = posts_count > ((page*app.config["POSTS_PER_PAGE"]) + app.config["POSTS_PER_PAGE"])

    author = db_session.query(Author).filter_by(username=author).one()
    if author.gravatar:
        author.gravatar_url = get_gravatar_url(author.gravatar)

    return render_template("index.html", posts=posts, now=datetime.datetime.now(), is_more=is_more, current_page=page, author=author)

@app.route("/<author>/<int:post_id>", methods=["GET"])
def get_author_post(author, post_id):
    try:
        post = db_session.query(Post).join(Author).filter(Author.username==author, Post.id==post_id, Post.draft==False).one()
    except Exception:
        app.logger.debug(format_exc)
        return abort(404)

    if post:
        post.views += 1

    db_session.commit()

    author = post.author
    if author.gravatar:
        author.gravatar_url = get_gravatar_url(author.gravatar)

    pid = request.args.get("pid", "0")

    return render_template("view.html", post=post, pid=pid, author=author)

@app.route("/<author>/<slug>", methods=["GET"])
def get_author_slug(author, slug):
    try:
        post = db_session.query(Post).join(Author).filter(Author.username==author, Post.slug==slug, Post.draft==False).one()
    except Exception:
        app.logger.debug(format_exc())
        return abort(404)

    if post:
        post.views += 1

    db_session.commit()

    author = post.author
    if author.gravatar:
        author.gravatar_url = get_gravatar_url(author.gravatar)

    pid = request.args.get("pid", "0")

    return render_template("view.html", post=post, pid=pid, author=author)

@app.route("/<author>/posts.rss", methods=["GET"])
def get_author_feed(author):

    return feed(author=author)

@app.route("/new", methods=["POST", "GET"])
@requires_authentication
def new_post():
    post = Post()
    post.title = request.form.get("title","untitled")
    post.author_id = session['user_id']
    post.slug = slugify(post.title)
    post.created_at = datetime.datetime.now()
    post.updated_at = datetime.datetime.now()

    db_session.add(post)
    db_session.commit()

    return redirect(url_for("edit", id=post.id))

@app.route("/preview/<int:id>", methods=["GET"])
@requires_authentication
def preview(id):
    try:
        post = db_session.query(Post).join(Author).filter(Author.id==session['user_id'], Post.id==id).one()
    except Exception:
        app.logger.debug(format_exc())
        return abort(404)

    return render_template("post_preview.html", post=post)

@app.route("/edit/<int:id>", methods=["GET","POST"])
@requires_authentication
def edit(id):
    try:
        post = db_session.query(Post).join(Author).filter(Author.id==session['user_id'], Post.id==id).one()
    except Exception:
        app.logger.debug(format_exc())
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

        db_session.commit()

        return redirect(url_for("edit", id=id))

@app.route("/save/<int:id>", methods=["POST"])
@requires_authentication
def save_post(id):
    try:
        post = db_session.query(Post).join(Author).filter(Author.id==session['user_id'], Post.id==id).one()
    except Exception:
        app.logger.debug(format_exc())
        return abort(404)
    if post.title != request.form.get("title", ""):
        post.title = request.form.get("title","")
        post.slug = slugify(post.title)
    post.text = request.form.get("content", "")
    post.updated_at = datetime.datetime.now()
    db_session.commit()

    return jsonify(success=True)

@app.route("/delete/<int:id>", methods=["GET","POST"])
@requires_authentication
def delete(id):
    try:
        post = db_session.query(Post).join(Author).filter(Author.id==session['user_id'], Post.id==id).one()
    except Exception:
        app.logger.debug(format_exc())
        flash("Error deleting post ID %s"%id, category="error")
    else:
        db_session.delete(post)
        db_session.commit()

    return redirect(request.args.get("next","") or request.referrer or url_for('index'))

@app.route("/admin", methods=["GET", "POST"])
@requires_authentication
def admin():
    drafts = db_session.query(Post).join(Author).filter(Author.id==session['user_id'], Post.draft==True).order_by(Post.created_at.desc()).all()
    posts  = db_session.query(Post).join(Author).filter(Author.id==session['user_id'], Post.draft==False).order_by(Post.created_at.desc()).all()

    return render_template("admin.html", drafts=drafts, posts=posts)

@app.route("/logout", methods=["GET"])
def logout():
    session.pop('user_name', None)
    session.pop('user_id', None)

    return abort(401)



if __name__ == "__main__":
    app.run()