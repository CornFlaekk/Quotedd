import flask
import flask_login
import sirope
import datetime

import utils.utils as utils

from model.QuoteDto import Quote
from model.UserDto import User
from model.QuoteListsDto import QuoteList
from model.CommentDto import Comment


quote_blueprint = flask.blueprints.Blueprint("quote", __name__,
                                       url_prefix="/quote",
                                       template_folder="templates",
                                       static_folder="static")
srp = sirope.Sirope()

# > ADD QUOTE <
@quote_blueprint.route("/add", methods=["POST"])
def add_quote():
    quote_content = flask.request.form.get("quoteContent")
    quote_book = flask.request.form.get("quoteBook")
    quote_author = flask.request.form.get("quoteAuthor")
    
    if len(quote_content) < 1:
        flask.flash("[E] Quote is empty")
        return flask.redirect("/home")
    elif len(quote_book) < 1:
        flask.flash("[E] Book is empty")
        return flask.redirect("/home")
    elif len(quote_author) < 1:
        flask.flash("[E] Author is empty")
        return flask.redirect("/home")
    
    quote_date = datetime.datetime.now()
    user = User.current()
    q = Quote(quote_content, quote_book, quote_author, quote_date, user.name)
    q.srp_save(srp)
    flask.flash("[S] Quote published")
    
    return flask.redirect("/home", 302)


# > DELETE QUOTE <
@quote_blueprint.route("/delete", methods=["GET"])
def delete_quote():
    user = flask_login.current_user
    quote_safe_id = flask.request.args.get("quoteSafeID")
    
    quote = srp.load(srp.oid_from_safe(quote_safe_id))
    
    if quote.user != user.name:
        flask.flash("[E] You can't delete a quote not yours")
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page, 302)
    else:
        
        #Delete this quote_link from Quotelists
        quotelists = list(srp.filter(QuoteList, lambda ql: quote_safe_id in ql.quote_ids))
        print("Quotelists afectadas: " + str(len(quotelists)))
        for quotelist in quotelists:
            quotelist.quote_ids.remove(quote_safe_id)
            srp.save(quotelist)     #Update DB
            
        #Delete all quotes from this quote
        comments = list(srp.filter(Comment, lambda c: c.quote_id == quote_safe_id))
        print("Comentarios afectados: " + str(len(comments)))
        for comment in comments:
            srp.delete(comment.oid)
        
        print(srp.delete(quote.oid))
        
        flask.flash("[S] Quote deleted")
        return flask.redirect("/home")


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
    
    back_link = flask.request.environ.get("HTTP_REFERER")
    print(back_link)
    values = {
        "quote" : quote,
        "user"  : user,
        "back_link" : back_link
    }
    return flask.render_template("quote_page.html", **values)


# > ADD COMMENT TO QUOTE <
@quote_blueprint.route("/comments/add", methods=["POST"])
def add_comment():
    quote_safe_id = flask.request.form.get("quoteSafeID")
    comment_content = flask.request.form.get("commentContent")
    
    if len(comment_content) < 1:
        flask.flash("[E] Comment is empty")
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page)
    
    comment_date = datetime.datetime.now()
    user = User.current()
    c = Comment(comment_content, quote_safe_id, comment_date, user.name)
    c.srp_save(srp)
    flask.flash("[S] Comment published")
    
    origin_page = flask.request.environ.get("HTTP_REFERER")
    return flask.redirect(origin_page, 302)