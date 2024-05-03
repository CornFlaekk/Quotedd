import flask
import flask_login
import sirope
import redis

from model.UserDto import User
from model.QuoteDto import Quote
from model.QuoteListsDto import QuoteList


import utils.utils as utils


search_blueprint = flask.blueprints.Blueprint("search", __name__,
                                       url_prefix="/search",
                                       template_folder="templates",
                                       static_folder="static")
redis_server = redis.Redis.from_url("rediss://red-cop97uacn0vc73doqavg:Gyj6VvZI4ERMYgHygGLNsANilOXHM4wr@frankfurt-redis.render.com:6379")
srp = sirope.Sirope(redis_obj=redis_server)


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
    
    
    len_quote_content = len(list(srp.filter(Quote, lambda q: search_query in q.content)))
    len_quote_author = len(list(srp.filter(Quote, lambda q: search_query in q.author)))
    len_quote_book = len(list(srp.filter(Quote, lambda q: search_query in q.book)))
    
    len_quotelist_name = len(list(srp.filter(QuoteList, lambda ql: search_query in ql.name)))
    len_quotelist_description = len(list(srp.filter(QuoteList, lambda ql: search_query in ql.description)))
    
    len_user_name = len(list(srp.filter(User, lambda u: search_query in u.name)))
    
    
    results = {
        len_quote_content : "quote_content",
        len_quote_author : "quote_author",
        len_quote_book : "quote_book",
        
        len_quotelist_name : "quotelist_name",
        len_quotelist_description : "quotelist_description",
        
        len_user_name : "user_name"
    }
    
    top_result_value = max(results.keys())
    top_result_string = results[top_result_value]
    
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
    
    
    search_quotes = list(srp.filter(Quote, lambda q: search_query in q.content))
    search_quotes = utils.set_quotes_quotelists(search_quotes, quotelists, srp)
    
    len_quote_content = len(list(srp.filter(Quote, lambda q: search_query in q.content)))
    len_quote_author = len(list(srp.filter(Quote, lambda q: search_query in q.author)))
    len_quote_book = len(list(srp.filter(Quote, lambda q: search_query in q.book)))
    len_quotelist_name = len(list(srp.filter(QuoteList, lambda ql: search_query in ql.name)))
    len_user_name = len(list(srp.filter(User, lambda u: search_query in u.name)))

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
    
    
    search_quotes = list(srp.filter(Quote, lambda q: search_query in q.author))
    search_quotes = utils.set_quotes_quotelists(search_quotes, quotelists, srp)
    
    len_quote_content = len(list(srp.filter(Quote, lambda q: search_query in q.content)))
    len_quote_author = len(list(srp.filter(Quote, lambda q: search_query in q.author)))
    len_quote_book = len(list(srp.filter(Quote, lambda q: search_query in q.book)))
    len_quotelist_name = len(list(srp.filter(QuoteList, lambda ql: search_query in ql.name)))
    len_user_name = len(list(srp.filter(User, lambda u: search_query in u.name)))
    
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
    
    
    search_quotes = list(srp.filter(Quote, lambda q: search_query in q.book))
    search_quotes = utils.set_quotes_quotelists(search_quotes, quotelists, srp)
    
    len_quote_content = len(list(srp.filter(Quote, lambda q: search_query in q.content)))
    len_quote_author = len(list(srp.filter(Quote, lambda q: search_query in q.author)))
    len_quote_book = len(list(srp.filter(Quote, lambda q: search_query in q.book)))
    len_quotelist_name = len(list(srp.filter(QuoteList, lambda ql: search_query in ql.name)))
    len_user_name = len(list(srp.filter(User, lambda u: search_query in u.name)))
    
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
    
    
    search_quotelists = list(srp.filter(QuoteList, lambda ql: search_query in ql.name))
    
    len_quote_content = len(list(srp.filter(Quote, lambda q: search_query in q.content)))
    len_quote_author = len(list(srp.filter(Quote, lambda q: search_query in q.author)))
    len_quote_book = len(list(srp.filter(Quote, lambda q: search_query in q.book)))
    len_quotelist_name = len(list(srp.filter(QuoteList, lambda ql: search_query in ql.name)))
    len_user_name = len(list(srp.filter(User, lambda u: search_query in u.name)))
    
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
    
    
    search_users = list(srp.filter(User, lambda u: search_query in u.name))
    
    len_quote_content = len(list(srp.filter(Quote, lambda q: search_query in q.content)))
    len_quote_author = len(list(srp.filter(Quote, lambda q: search_query in q.author)))
    len_quote_book = len(list(srp.filter(Quote, lambda q: search_query in q.book)))
    len_quotelist_name = len(list(srp.filter(QuoteList, lambda ql: search_query in ql.name)))
    len_user_name = len(list(srp.filter(User, lambda u: search_query in u.name)))
    
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