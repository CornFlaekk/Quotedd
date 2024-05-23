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


# > EDIT QUOTE <
@quote_blueprint.route("/edit", methods=["POST"])
def edit_quote():
    user = flask_login.current_user
    
    quote_content = flask.request.form.get("quote-content")
    quote_book = flask.request.form.get("quote-book")
    quote_author = flask.request.form.get("quote-author")
    quote_safe_id = flask.request.form.get("quote-safe-id")
    
    if len(quote_content) < 1:
        flask.flash("[E] Quote is empty")
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page, 302)
    elif len(quote_book) < 1:
        flask.flash("[E] Book is empty")
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page, 302)
    elif len(quote_author) < 1:
        flask.flash("[E] Author is empty")
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page, 302)
    
    
    quote = srp.load(srp.oid_from_safe(quote_safe_id))
    
    # If invalid user tries to edit    
    if quote.user != user.name:
        flask.flash("[E] Edit not allowed on others quotes")
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page, 302)

    quote.set_content(quote_content)
    quote.set_book(quote_book)
    quote.set_author(quote_author)
    
    srp.save(quote)
    flask.flash("[S] Quote updated")
    
    origin_page = flask.request.environ.get("HTTP_REFERER")
    return flask.redirect(origin_page, 302)
        


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
        for quotelist in quotelists:
            quotelist.quote_ids.remove(quote_safe_id)
            srp.save(quotelist)     #Update DB
            
        #Delete all comments from this quote
        comments = list(srp.filter(Comment, lambda c: c.quote_id == quote_safe_id))
        for comment in comments:
            srp.delete(comment.oid)
        
        srp.delete(quote.oid)
        
        flask.flash("[S] Quote deleted")
        return flask.redirect("/home")


# > VIEW QUOTE PAGE <
@quote_blueprint.route("", methods=["GET"])
def quote_page():
    user = flask_login.current_user
    
    quote_safe_id = flask.request.args.get("quoteSafeID")
    quote_oid = srp.oid_from_safe(quote_safe_id)
    
    if quote_oid is None:
        flask.flash("[E] Quote not found")
        return flask.redirect("/home")
    
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
        comment.safe_id = srp.safe_from_oid(comment.oid)
    quote.comments = comments
    
    back_link = flask.request.environ.get("HTTP_REFERER")
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

# > EDIT COMMENT CONTENT <
@quote_blueprint.route("/comments/edit", methods=["POST"])
def edit_comment():
    comment_safe_id = flask.request.form.get("comment-safe-id")
    comment_content = flask.request.form.get("comment-content")
    
    if len(comment_content) < 1:
        flask.flash("[E] Comment is empty")
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page)
    
    
    comment = srp.load(srp.oid_from_safe(comment_safe_id))
    
    user = flask_login.current_user
    
    # If invalid user tries to edit    
    if comment.user != user.name:
        flask.flash("[E] Edit not allowed on others comments")
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page, 302)

    comment.set_content(comment_content)
    srp.save(comment)
    flask.flash("[S] Comment updated")
    
    origin_page = flask.request.environ.get("HTTP_REFERER")
    return flask.redirect(origin_page, 302)


# > DELETE COMMENT <
@quote_blueprint.route("/comments/delete", methods=["GET"])
def delete_comment():
    user = flask_login.current_user
    comment_safe_id = flask.request.args.get("commentSafeID")
    
    comment = srp.load(srp.oid_from_safe(comment_safe_id))
    
    if comment.user != user.name:
        flask.flash("[E] You can't delete a comment not yours")
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page, 302)
    else:
        
        srp.delete(comment.oid)
        flask.flash("[S] Comment deleted")
        
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page, 302)