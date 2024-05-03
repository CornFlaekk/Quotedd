import flask
import flask_login
import sirope
import json
import datetime
import redis

import utils.utils as utils 

from model.UserDto import User
from model.QuoteDto import Quote
from model.QuoteListsDto import QuoteList


main_blueprint = flask.blueprints.Blueprint("main", __name__,
                                       url_prefix="",
                                       template_folder="templates",
                                       static_folder="static")
redis_server = redis.Redis.from_url("rediss://red-cop97uacn0vc73doqavg:Gyj6VvZI4ERMYgHygGLNsANilOXHM4wr@frankfurt-redis.render.com:6379")
srp = sirope.Sirope(redis_obj=redis_server)



@main_blueprint.route("/", methods=["GET"])
def main():
    user = User.current()
    print(user)
    if user is None:
        return flask.send_from_directory(main_blueprint.static_folder, "index.html")
    else:
        return flask.redirect("/home")


# > LOGIN <
@main_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.send_from_directory(main_blueprint.static_folder, "login.html")
    else:
        user_name = flask.request.form.get("userName")
        user_password = flask.request.form.get("userPassword")
        user = User.find(srp, user_name)
        
        if user is None or not user.compare_passwd(user_password):
            flask.flash("Incorrect login credentials")
            return flask.redirect("/login")
        else:
            flask.flash("Login successful")
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
        return flask.send_from_directory(main_blueprint.static_folder, "register.html")
    else:
        user_name = flask.request.form.get("userName")
        user_email = flask.request.form.get("userEmail")
        user_password = flask.request.form.get("userPassword")
        
        u = User(user_name, user_email, user_password)
        srp.save(u)
        flask.flash("User registered")
        return flask.redirect("/login")


# > HOME PAGE <
@flask_login.login_required
@main_blueprint.route("/home", methods=["GET"])
def home():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    last_quotes = list(srp.load_last(Quote, 10))
    quotelists = list(srp.filter(QuoteList, lambda ql: ql.user == user.name))
    
    last_quotes = utils.set_quotes_quotelists(last_quotes, quotelists, srp) 
        
        
    values = {
        "last_quotes" : last_quotes,
        "user" : user
    }
    
    return flask.render_template("home.html", **values)
