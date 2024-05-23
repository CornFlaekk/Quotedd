import flask
import flask_login
import sirope
import json
import datetime

import utils.utils as utils 

from model.UserDto import User
from model.QuoteDto import Quote
from model.QuoteListsDto import QuoteList


main_blueprint = flask.blueprints.Blueprint("main", __name__,
                                       url_prefix="",
                                       template_folder="templates",
                                       static_folder="static")
srp = sirope.Sirope()



@main_blueprint.route("/", methods=["GET"])
def main():
    user = User.current()
    print(user)
    if user is None:
        return flask.render_template("index.html")
    else:
        return flask.redirect("/home")


# > LOGIN <
@main_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.render_template("login.html")
    else:
        user_name = flask.request.form.get("userName")
        user_password = flask.request.form.get("userPassword")
        
        if len(user_name) < 1:
            flask.flash("[E] Username is empty")
            return flask.redirect("/login")
        elif len(user_password) < 1:
            flask.flash("[E] Password is empty")
            return flask.redirect("/login")
        
        user = User.find(srp, user_name)
        
        if user is None or not user.compare_passwd(user_password):
            flask.flash("[E] Incorrect login credentials")
            return flask.redirect("/login")
        else:
            flask.flash("[S] Login successful")
            flask_login.login_user(user, force=True)
            return flask.redirect("/home")


# > LOGOUT <
@flask_login.login_required
@main_blueprint.route("/logout", methods=["GET"])
def logout():
    flask_login.logout_user()
    return flask.redirect("/")


# > REGISTER <
@main_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "GET":
        return flask.render_template("register.html")
    else:
        user_name = flask.request.form.get("userName")
        user_email = flask.request.form.get("userEmail")
        user_password = flask.request.form.get("userPassword")
        
        if len(user_name) < 3:
            flask.flash("[E] Username needs to have at least 3 letters")
            return flask.redirect("/register")
        elif (len(user_email) < 3) or ('@' not in user_email) or ('.' not in user_email):
            flask.flash("[E] Email not valid")
            return flask.redirect("/register")
        elif len(user_password) < 3:
            flask.flash("[E] Password needs to have at least 3 letters")
            return flask.redirect("/register")
        
        if len(list(srp.filter(User, lambda u: u.name == user_name))):
            flask.flash("[E] Username already registered")
            return flask.redirect("/register")
        elif(len(list(srp.filter(User, lambda u: u.email == user_email)))):
            flask.flash("[E] Email already registered")
            return flask.redirect("/register")
        
        u = User(user_name, user_email, user_password)
        srp.save(u)
        flask.flash("[S] User registered")
        return flask.render_template("login.html")


# > HOME PAGE <
@flask_login.login_required
@main_blueprint.route("/home", methods=["GET"])
def home():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    page = flask.request.args.get("page")
    if page == '0':
        return flask.redirect("/home")
    if page is None:
        page = 0
    page = int(page)
    
    last_quotes = list(srp.load_all(Quote))
    last_quotes.sort(key= lambda q : q.date, reverse=True)      #Order by most recent ones
    n_quotes = 10
        
    # Calculate the max page index
    total_pages = (len(last_quotes) // n_quotes)
    if len(last_quotes) % n_quotes == 0:
        total_pages = (len(last_quotes) // n_quotes) -1

    
    #If try to access page with no entries -> go back to last page
    if (page > total_pages):
        page = total_pages
        return flask.redirect(f"/home?page={page}")
    
    last_quotes = last_quotes[page * n_quotes : page * n_quotes + n_quotes]       #Only show Quotes on current page (Pagination)
    quotelists = list(srp.filter(QuoteList, lambda ql: ql.user == user.name))
    
    last_quotes = utils.set_quotes_quotelists(last_quotes, quotelists, srp)
        
    values = {
        "last_quotes" : last_quotes,
        "user" : user,
        "page" : page,
        "total_pages" : total_pages
    }
    
    return flask.render_template("home.html", **values)
