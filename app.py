import flask
import flask_login
import sirope
import json
import datetime
import redis

from model.UserDto import User
from model.QuoteDto import Quote
from model.QuoteListsDto import QuoteList
from model.CommentDto import Comment

import views.quote.quote_view as quote_view
import views.main.main_view as main_view
import views.quotelist.quotelist_view as quotelist_view
import views.search.search_view as search_view

def create_app():
    lmanager = flask_login.login_manager.LoginManager()
    flapp = flask.Flask(__name__)
    sirp = sirope.Sirope()
    
    redis_server = redis.Redis.from_url("rediss://red-cop97uacn0vc73doqavg:Gyj6VvZI4ERMYgHygGLNsANilOXHM4wr@frankfurt-redis.render.com:6379")
    sirp = sirope.Sirope(redis_obj=redis_server)
    
    flapp.config.from_file("instance/config.json", load=json.load)
    lmanager.init_app(flapp)
    
    flapp.register_blueprint(main_view.main_blueprint) 
    flapp.register_blueprint(quote_view.quote_blueprint)
    flapp.register_blueprint(quotelist_view.quotelist_blueprint)
    flapp.register_blueprint(search_view.search_blueprint)
    
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