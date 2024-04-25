import flask
import flask_login
import sirope

from model.QuoteListsDto import QuoteList
from model.QuoteDto import Quote


quotelist_blueprint = flask.blueprints.Blueprint("quotelist", __name__,
                                       url_prefix="/quotelist",
                                       template_folder="templates",
                                       static_folder="static")
srp = sirope.Sirope()

# VIEW QUOTELISTS
@flask_login.login_required
@quotelist_blueprint.route("", methods=["GET"])
def quotelists():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    quotelists = list(srp.filter(QuoteList, lambda ql: ql.user == user.name))
    
    for quotelist in quotelists:
        quotelist.quotes = []
        for quote_id in quotelist.quote_ids:
            quote_oid = srp.oid_from_safe(quote_id)
            quote = srp.load(quote_oid)
            quote.safe_id = quote_id
            quotelist.quotes.append(quote)
    
    values = {
        "quotelists"  :quotelists,
        "user" : user
    }
    
    return flask.render_template("quotelist.html", **values)
