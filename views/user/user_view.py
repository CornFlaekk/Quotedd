import flask
import flask_login
import sirope
import datetime

import utils.utils as utils

from model.QuoteDto import Quote
from model.UserDto import User
from model.QuoteListsDto import QuoteList
from model.CommentDto import Comment


user_blueprint = flask.blueprints.Blueprint("user", __name__,
                                       url_prefix="/user",
                                       template_folder="templates",
                                       static_folder="static")
srp = sirope.Sirope()


# VIEW USER PROFILE
@user_blueprint.route("", methods=["GET"])
def user_profile():
    user = flask_login.current_user
    
    user_name = flask.request.args.get("username")
    user_profile = list(srp.filter(User, lambda u: u.name == user_name))[0]
    
    user_profile.quotes = list(srp.filter(Quote, lambda q : q.user == user_profile.name))
    for quote in user_profile.quotes:
        quote.safe_id = srp.safe_from_oid(quote.oid)
    
    user_profile.quotelists = list(srp.filter(QuoteList, lambda ql : ql.user == user_profile.name))
    for quotelist in user_profile.quotelists:
        quotelist.safe_id = srp.safe_from_oid(quotelist.oid)
    
    
    values = {
        "user" : user,
        "user_profile" : user_profile
    }
    
    return flask.render_template("user_page.html", **values)