import flask
import flask_login
import sirope
import json
import datetime

from model.UserDto import User
from model.QuoteDto import Quote
from model.QuoteListsDto import QuoteList
from model.CommentDto import Comment

import views.quote.quote_view as quote_view
import views.main.main_view as main_view

def create_app():
    lmanager = flask_login.login_manager.LoginManager()
    flapp = flask.Flask(__name__)
    sirp = sirope.Sirope()
    
    flapp.config.from_file("instance/config.json", load=json.load)
    lmanager.init_app(flapp)
    
    flapp.register_blueprint(main_view.main_blueprint) 
    flapp.register_blueprint(quote_view.quote_blueprint)
    
    return flapp, lmanager, sirp

app, lm, srp = create_app()


@lm.user_loader
def user_loader(username: str) -> User:
    return User.find(srp, username)


@lm.unauthorized_handler
def unauthorized_handler():
    flask.flash("Unauthorized user")
    return flask.redirect("/login")


if __name__ == "__main__":
       flask.run()