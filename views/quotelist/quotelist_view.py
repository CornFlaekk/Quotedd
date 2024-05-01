import flask
import flask_login
import sirope
import redis

from model.QuoteListsDto import QuoteList
from model.QuoteDto import Quote

quotelist_blueprint = flask.blueprints.Blueprint("quotelist", __name__,
                                       url_prefix="/quotelist",
                                       template_folder="templates",
                                       static_folder="static")
redis_server = redis.Redis(host="red-cop97uacn0vc73doqavg", port=6379)
srp = sirope.Sirope(redis_obj=redis_server)

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
        quotelist.safe_id = srp.safe_from_oid(quotelist.oid)
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

# DELETE QUOTELIST
@flask_login.login_required
@quotelist_blueprint.route("/delete", methods=["GET"])
def delete():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    quotelist_safe_id = flask.request.args.get("quotelistSafeID")
    user_id = user.get_id()
    quotelists_returned = list(srp.filter(QuoteList, lambda ql: ql.get_safe_id(srp) == quotelist_safe_id and ql.user == user_id))
    quotelist = quotelists_returned[0]
    
    if quotelist is None:
        flask.flash("Quotelist not found")
    
    else:
        quotelist_oid = srp.oid_from_safe(quotelist_safe_id)
        srp.delete(quotelist_oid)
        flask.flash("Quotelist deleted")
    
    origin_page = flask.request.environ.get("HTTP_REFERER")
    return flask.redirect(origin_page, 302)
    
    
# > ADD QUOTELIST <
@flask_login.login_required
@quotelist_blueprint.route("/add", methods=["POST"])
def add_quotelist():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    quotelist_name = flask.request.form.get("quotelistName")
    quotelist_desc = flask.request.form.get("quotelistDesc")
    
    ql = QuoteList(quotelist_name, quotelist_desc, user.name)
    ql.srp_save(srp)
    
    origin_page = flask.request.environ.get("HTTP_REFERER")
    return flask.redirect(origin_page, 302)


# > ADD QUOTE TO QUOTELIST <
@flask_login.login_required
@quotelist_blueprint.route("/add_quote", methods=["GET"])
def add_quote_quotelist():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    quotelist_name = flask.request.args.get("quotelistName")
    quote_safe_id = flask.request.args.get("quoteSafeID")
    
    if quotelist_name[:2] == "✓ ":
        quotelist_name = quotelist_name[2:]
        print(quotelist_name)
    
    quotelist = srp.find_first(QuoteList, lambda ql: ql.name == quotelist_name)     
    
    if quote_safe_id in quotelist.quote_ids:
        quotelist.remove_quote_id(quote_safe_id)
        quotelist.srp_save(srp)
    else:
        quotelist.add_quote_id(quote_safe_id)
        quotelist.srp_save(srp)
        
    origin_page = flask.request.environ.get("HTTP_REFERER")
    return flask.redirect(origin_page, 302)