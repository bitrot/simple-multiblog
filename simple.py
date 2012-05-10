import re
import datetime
import markdown
from werkzeug.security import check_password_hash
from unicodedata import normalize
from model import Post, User
from flaskext.oauth import OAuth
from flaskext.sqlalchemy import SQLAlchemy
from flask import render_template, request, Flask, flash, redirect, url_for, abort, jsonify, Response as response, make_response
from functools import wraps
from traceback import format_exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
try:
    from settings import BACKEND
    Engine = create_engine(BACKEND)
    Session = sessionmaker(bind=Engine)
except ImportError:
    print "You need to create the settings file before you can run simple-multiblog!"

app = Flask(__name__)
app.config.from_object('settings')

# TODO: Add error level email handler

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def requires_authentication(f):
    @wraps(f)
    def _auth_decorator(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return response("Could not authenticate you", 401, {"WWW-Authenticate":'Basic realm="Login Required"'})
        else:
            try:
                session = Session()
                user = session.query(User).filter_by(username=auth.username).first()
                session.close()
            except Exception:
                app.logger.debug(format_exc())
                return response("Could not authenticate you", 401, {"WWW-Authenticate":'Basic realm="Login Required"'})

            if not check_password_hash(user.password, auth.password):
                return response("Could not authenticate you", 401, {"WWW-Authenticate":'Basic realm="Login Required"'})

        return f(*args, **kwargs)

    return _auth_decorator

@app.route("/")
def index():
    page = request.args.get("page", 0, type=int)
    session = Session()
    posts_master = session.query(Post).filter_by(draft=False).order_by(Post.created_at.desc())
    session.close()
    posts_count = posts_master.count()

    posts = posts_master.limit(app.config["POSTS_PER_PAGE"]).offset(page*app.config["POSTS_PER_PAGE"]).all()
    is_more = posts_count > ((page*app.config["POSTS_PER_PAGE"]) + app.config["POSTS_PER_PAGE"])

    return render_template("index.html", posts=posts, now=datetime.datetime.now(),
                                         is_more=is_more, current_page=page)

@app.route("/<author>") # all posts by author
def view_post_by_author(author):
    page = request.args.get("page", 0, type=int)
    try:
        session = Session()
        posts_master = session.query(Post).filter_by(draft=False, author=author).order_by(Post.created_at.desc())
        session.close()
    except Exception:
        app.logger.debug(format_exc())
        return abort(404)
    posts_count = posts_master.count()

    posts = posts_master.limit(app.config["POSTS_PER_PAGE"]).offset(page*app.config["POSTS_PER_PAGE"]).all()
    is_more = posts_count > ((page*app.config["POSTS_PER_PAGE"]) + app.config["POSTS_PER_PAGE"])

    return render_template("index.html", posts=posts, now=datetime.datetime.now(),
        is_more=is_more, current_page=page)

@app.route("/<int:post_id>")
def view_post(post_id):
    try:
        session = Session()
        post = session.query(Post).filter_by(id=post_id, draft=False).one()
        session.close()
    except Exception:
        app.logger.debug(format_exc())
        return abort(404)

    session = Session()
    session.query(Post).filter_by(id=post_id).update({Post.views:Post.views+1})
    session.commit()
    session.close()

    return render_template("view.html", post=post)

@app.route("/<slug>")
def view_post_slug(slug):
    try:
        session = Session()
        post = session.query(Post).filter_by(slug=slug,draft=False).one()
        session.close()
    except Exception:
        app.logger.debug(format_exc())
        return abort(404)

    session = Session()
    session.query(Post).filter_by(slug=slug).update({Post.views:Post.views+1})
    session.commit()
    session.close()

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

    session = Session()
    session.add(post)
    session.commit()
    session.close()

    return redirect(url_for("edit", id=post.id))

@app.route("/edit/<int:id>", methods=["GET","POST"])
@requires_authentication
def edit(id):
    try:
        session = Session()
        post = session.query(Post).filter_by(id=id).one()
        session.close()
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

        session = Session()
        session.add(post)
        session.commit()
        session.close()

        return redirect(url_for("edit", id=id))

@app.route("/delete/<int:id>", methods=["GET","POST"])
@requires_authentication
def delete(id):
    try:
        session = Session()
        post = session.query(Post).filter_by(id=id).one()
        session.close()
    except Exception:
        app.logger.debug(format_exc())
        flash("Error deleting post ID %s"%id, category="error")
    else:
        session = Session()
        session.delete(post)
        session.commit()
        session.close()

    return redirect(request.args.get("next","") or request.referrer or url_for('index'))

@app.route("/admin", methods=["GET", "POST"])
@requires_authentication
def admin():
    session = Session()
    drafts = session.query(Post).filter_by(draft=True)\
                                          .order_by(Post.created_at.desc()).all()
    posts  = session.query(Post).filter_by(draft=False)\
                                          .order_by(Post.created_at.desc()).all()
    session.close()
    return render_template("admin.html", drafts=drafts, posts=posts)

@app.route("/admin/save/<int:id>", methods=["POST"])
@requires_authentication
def save_post(id):
    try:
        session = Session()
        post = session.query(Post).filter_by(id=id).one()
        session.close()
    except Exception:
        app.logger.debug(format_exc())
        return abort(404)
    if post.title != request.form.get("title", ""):
        post.title = request.form.get("title","")
        post.slug = slugify(post.title)
    post.text = request.form.get("content", "")
    post.updated_at = datetime.datetime.now()
    session = Session()
    session.add(post)
    session.commit()
    session.close()
    return jsonify(success=True)

@app.route("/preview/<int:id>")
@requires_authentication
def preview(id):
    try:
        session = Session()
        post = session.query(Post).filter_by(id=id).one()
        session.close()
    except Exception:
        app.logger.debug(format_exc())
        return abort(404)

    return render_template("post_preview.html", post=post)

@app.route("/posts.rss")
def feed():
    session = Session()
    posts = session.query(Post).filter_by(draft=False).order_by(Post.created_at.desc()).limit(10).all()
    session.close()

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