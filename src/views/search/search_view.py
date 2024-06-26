import flask
import flask_login
import sirope

from model.UserDto import User
from model.QuoteDto import Quote
from model.QuoteListsDto import QuoteList

import utils.utils as utils


search_blueprint = flask.blueprints.Blueprint("search", __name__,
                                       url_prefix="/search",
                                       template_folder="templates",
                                       static_folder="static")
srp = sirope.Sirope()


# MAIN Search Page -> Redirects to page with most results
@search_blueprint.route("", methods=["GET"])
def search():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    search_query = flask.request.args.get("searchQuery")
    if search_query is None:
        search_query = ""
    
    
    len_quote_content = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.content.lower())))
    len_quote_author = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.author.lower())))
    len_quote_book = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.book.lower())))
    
    len_quotelist_name = len(list(srp.filter(QuoteList, lambda ql: search_query.lower() in ql.name.lower())))
    
    len_user_name = len(list(srp.filter(User, lambda u: search_query.lower() in u.name.lower())))
    
    
    results = {
        len_quote_content : "quote_content",
        len_quote_author : "quote_author",
        len_quote_book : "quote_book",
        
        len_quotelist_name : "quotelist_name",
        
        len_user_name : "user_name"
    }
    
    top_result_value = max(results.keys())
    top_result_string = results[top_result_value]
    
    if len_quote_content == 0 and len_quote_author == 0 and len_quote_book == 0 and len_quotelist_name == 0 and len_user_name == 0 :
        flask.flash("[W] No results found")
    
    if len(search_query) == 0:
        len_quote_content = 0
        len_quote_author = 0
        len_quote_book = 0
        len_quotelist_name = 0
        len_user_name = 0
        top_result_string = "quote_content"
    
        
    return flask.redirect(f"/search/{top_result_string}/?searchQuery={search_query}")


# SEARCH by Quote Content
@search_blueprint.route("/quote_content/")
def search_quote_content():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    quotelists = list(srp.filter(QuoteList, lambda ql: ql.user == user.name))
    
    search_query = flask.request.args.get("searchQuery")
    
    
    search_quotes = list(srp.filter(Quote, lambda q: search_query.lower() in q.content.lower()))
    search_quotes = utils.set_quotes_quotelists(search_quotes, quotelists, srp)
    
    len_quote_content = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.content.lower())))
    len_quote_author = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.author.lower())))
    len_quote_book = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.book.lower())))
    len_quotelist_name = len(list(srp.filter(QuoteList, lambda ql: search_query.lower() in ql.name.lower())))
    len_user_name = len(list(srp.filter(User, lambda u: search_query.lower() in u.name.lower())))

    if len(search_query) == 0:
        search_quotes = list()
        len_quote_content = 0
        len_quote_author = 0
        len_quote_book = 0
        len_quotelist_name = 0
        len_user_name = 0
    
    database_results = {
        "quote_content" : len_quote_content,
        "quote_author" : len_quote_author,
        "quote_book" : len_quote_book,
        "quotelist_name" : len_quotelist_name,
        "user_name" : len_user_name
    }
    
    
    values = {
        "user" : user,
        "search_type" : "quotes",
        "search_current" : "quote_content",
        "search_quotes" : search_quotes,
        "search_query" : search_query,
        
        "database_results" : database_results
    }
    
    return flask.render_template("search_page.html", **values)


# SEARCH by Quote Author
@search_blueprint.route("/quote_author/")
def search_quote_author():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    quotelists = list(srp.filter(QuoteList, lambda ql: ql.user == user.name))
        
    search_query = flask.request.args.get("searchQuery")
    
    
    search_quotes = list(srp.filter(Quote, lambda q: search_query.lower() in q.author.lower()))
    search_quotes = utils.set_quotes_quotelists(search_quotes, quotelists, srp)
    
    len_quote_content = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.content.lower())))
    len_quote_author = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.author.lower())))
    len_quote_book = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.book.lower())))
    len_quotelist_name = len(list(srp.filter(QuoteList, lambda ql: search_query.lower() in ql.name.lower())))
    len_user_name = len(list(srp.filter(User, lambda u: search_query.lower() in u.name.lower())))
    
    if len(search_query) == 0:
        search_quotes = list()
        len_quote_content = 0
        len_quote_author = 0
        len_quote_book = 0
        len_quotelist_name = 0
        len_user_name = 0
    
    database_results = {
        "quote_content" : len_quote_content,
        "quote_author" : len_quote_author,
        "quote_book" : len_quote_book,
        "quotelist_name" : len_quotelist_name,
        "user_name" : len_user_name
    }
    
    values = {
        "user" : user,
        "search_type" : "quotes",
        "search_current" : "quote_author",
        "search_quotes" : search_quotes,
        "search_query" : search_query,
        
        "database_results" : database_results
    }
    
    return flask.render_template("search_page.html", **values)


# SEARCH by Quote Book
@search_blueprint.route("/quote_book/")
def search_quote_book():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    quotelists = list(srp.filter(QuoteList, lambda ql: ql.user == user.name))
        
    search_query = flask.request.args.get("searchQuery")
    
    
    search_quotes = list(srp.filter(Quote, lambda q: search_query.lower() in q.book.lower()))
    search_quotes = utils.set_quotes_quotelists(search_quotes, quotelists, srp)
    
    len_quote_content = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.content.lower())))
    len_quote_author = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.author.lower())))
    len_quote_book = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.book.lower())))
    len_quotelist_name = len(list(srp.filter(QuoteList, lambda ql: search_query.lower() in ql.name.lower())))
    len_user_name = len(list(srp.filter(User, lambda u: search_query.lower() in u.name.lower())))
    
    if len(search_query) == 0:
        search_quotes = list()
        len_quote_content = 0
        len_quote_author = 0
        len_quote_book = 0
        len_quotelist_name = 0
        len_user_name = 0
    
    database_results = {
        "quote_content" : len_quote_content,
        "quote_author" : len_quote_author,
        "quote_book" : len_quote_book,
        "quotelist_name" : len_quotelist_name,
        "user_name" : len_user_name
    }
    
    values = {
        "user" : user,
        "search_type" : "quotes",
        "search_current" : "quote_book",
        "search_quotes" : search_quotes,
        "search_query" : search_query,
        
        "database_results" : database_results
    }
    
    return flask.render_template("search_page.html", **values)


# SEARCH by Quotelist
@search_blueprint.route("/quotelist_name/")
def search_quotelist_name():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    quotelists = list(srp.filter(QuoteList, lambda ql: ql.user == user.name))
    
    search_query = flask.request.args.get("searchQuery")
    
    
    search_quotelists = list(srp.filter(QuoteList, lambda ql: search_query.lower() in ql.name.lower()))
    
    for quotelist in search_quotelists:
        quotelist.safe_id = srp.safe_from_oid(quotelist.oid)
    
    len_quote_content = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.content.lower())))
    len_quote_author = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.author.lower())))
    len_quote_book = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.book.lower())))
    len_quotelist_name = len(list(srp.filter(QuoteList, lambda ql: search_query.lower() in ql.name.lower())))
    len_user_name = len(list(srp.filter(User, lambda u: search_query.lower() in u.name.lower())))
    
    if len(search_query) == 0:
        search_quotelists = list()
        len_quote_content = 0
        len_quote_author = 0
        len_quote_book = 0
        len_quotelist_name = 0
        len_user_name = 0
    
    database_results = {
        "quote_content" : len_quote_content,
        "quote_author" : len_quote_author,
        "quote_book" : len_quote_book,
        "quotelist_name" : len_quotelist_name,
        "user_name" : len_user_name
    }
    
    values = {
        "user" : user,
        "search_type" : "quotelists",
        "search_current" : "quotelist_name",
        "search_quotelists" : search_quotelists,
        "search_query" : search_query,
        
        "database_results" : database_results
    }
    
    return flask.render_template("search_page.html", **values)


# SEARCH by User
@search_blueprint.route("/user_name/")
def search_user_name():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    quotelists = list(srp.filter(QuoteList, lambda ql: ql.user == user.name))
    
    search_query = flask.request.args.get("searchQuery")
    
    
    search_users = list(srp.filter(User, lambda u: search_query.lower() in u.name.lower()))
    
    len_quote_content = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.content.lower())))
    len_quote_author = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.author.lower())))
    len_quote_book = len(list(srp.filter(Quote, lambda q: search_query.lower() in q.book.lower())))
    len_quotelist_name = len(list(srp.filter(QuoteList, lambda ql: search_query.lower() in ql.name.lower())))
    len_user_name = len(list(srp.filter(User, lambda u: search_query.lower() in u.name.lower())))
    
    if len(search_query) == 0:
        search_users = list()
        len_quote_content = 0
        len_quote_author = 0
        len_quote_book = 0
        len_quotelist_name = 0
        len_user_name = 0
    
    database_results = {
        "quote_content" : len_quote_content,
        "quote_author" : len_quote_author,
        "quote_book" : len_quote_book,
        "quotelist_name" : len_quotelist_name,
        "user_name" : len_user_name
    }
    
    values = {
        "user" : user,
        "search_type" : "users",
        "search_current" : "user_name",
        "search_users" : search_users,
        "search_query" : search_query,
        
        "database_results" : database_results
    }
    
    return flask.render_template("search_page.html", **values)