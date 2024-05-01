import flask
import flask_login
import sirope
import datetime
import redis

import utils.utils as utils

from model.QuoteDto import Quote
from model.UserDto import User
from model.QuoteListsDto import QuoteList
from model.CommentDto import Comment


quote_blueprint = flask.blueprints.Blueprint("quote", __name__,
                                       url_prefix="/quote",
                                       template_folder="templates",
                                       static_folder="static")
redis_server = redis.Redis(host="redis://red-cop97uacn0vc73doqavg", port=6379)
srp = sirope.Sirope(redis_obj=redis_server)

# > ADD QUOTE <
@quote_blueprint.route("/add", methods=["POST"])
def add_quote():
    quote_content = flask.request.form.get("quoteContent")
    quote_book = flask.request.form.get("quoteBook")
    quote_author = flask.request.form.get("quoteAuthor")
    quote_date = datetime.datetime.now()
    user = User.current()
    q = Quote(quote_content, quote_book, quote_author, quote_date, user.name)
    q.srp_save(srp)
    
    return flask.redirect("/home", 302)

# > VIEW QUOTE PAGE <
@quote_blueprint.route("", methods=["GET"])
def quote_page():
    user = flask_login.current_user
    
    quote_safe_id = flask.request.args.get("quoteSafeID")
    quote_oid = srp.oid_from_safe(quote_safe_id)
    quote = srp.load(quote_oid)
    quote.safe_id = quote_safe_id
    quote.time_elapsed = utils.time_elapsed(quote.date)
    
    quotelists = list(srp.filter(QuoteList, lambda ql: ql.user == user.name))
    quote.quotelists_names = []
    for quotelist in quotelists:
            if quote.safe_id in quotelist.quote_ids:
                name = f"✓ {quotelist.name}"
                quote.quotelists_names.append(name)
            else:
                quote.quotelists_names.append(quotelist.name)
                
    comments = list(srp.filter(Comment, lambda c: c.quote_id == quote.safe_id))
    for comment in comments:
        comment.time_elapsed = utils.time_elapsed(comment.date)
    quote.comments = comments
                    
    values = {
        "quote" : quote,
        "user"  : user
    }
    return flask.render_template("quote_page.html", **values)


# > ADD COMMENT TO QUOTE <
@quote_blueprint.route("/comments/add", methods=["POST"])
def add_comment():
    quote_safe_id = flask.request.form.get("quoteSafeID")
    comment_content = flask.request.form.get("commentContent")
    comment_date = datetime.datetime.now()
    user = User.current()
    c = Comment(comment_content, quote_safe_id, comment_date, user.name)
    c.srp_save(srp)
    
    origin_page = flask.request.environ.get("HTTP_REFERER")
    return flask.redirect(origin_page, 302)