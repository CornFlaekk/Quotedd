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


#VIEW QUOTELIST
@flask_login.login_required
@quotelist_blueprint.route("", methods=["GET"])
def quotelist():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    quotelist_safe_id = flask.request.args.get("quotelistSafeID")
    quotelist_id = srp.oid_from_safe(quotelist_safe_id)
    if quotelist_id is None:
        flask.flash("[E] Quotelist not found")
        return flask.redirect("/home")
    
    quotelist = srp.load(quotelist_id)
    quotelist.safe_id = quotelist_safe_id
    quotelist.quotes = []
    for quote_id in quotelist.quote_ids:
            quote_oid = srp.oid_from_safe(quote_id)
            quote = srp.load(quote_oid)
            quote.safe_id = quote_id
            quotelist.quotes.append(quote)
    
    back_link = flask.request.environ.get("HTTP_REFERER")

    values = {
        "quotelist" : quotelist,
        "user" : user,
        "back_link" : back_link
    }

    return flask.render_template("quotelist.html", **values)
    

# VIEW YOUR QUOTELISTS
@flask_login.login_required
@quotelist_blueprint.route("/i", methods=["GET"])
def my_quotelists():
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
    
    return flask.render_template("your_quotelists.html", **values)

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
    quotelist = srp.load(srp.oid_from_safe(quotelist_safe_id))
    
    if user.name != quotelist.user:
        flask.flash("[E] Delete not allowed on others QuoteLists")
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page, 302)
    
    if quotelist is None:
        flask.flash("[E] Quotelist not found")
    
    else:
        quotelist_oid = srp.oid_from_safe(quotelist_safe_id)
        srp.delete(quotelist_oid)
        flask.flash("[S] Quotelist deleted")
    
    origin_page = flask.request.environ.get("HTTP_REFERER")
    if "/quotelist?quotelistSafeID=" in origin_page:
        return flask.redirect("/home")
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
    
    if len(quotelist_name) < 1:
        flask.flash("[E] Quotelist name is empty")
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page, 302)
    
    ql = QuoteList(quotelist_name, quotelist_desc, user.name)
    ql.srp_save(srp)
    flask.flash("[S] Quotelist created")
    
    origin_page = flask.request.environ.get("HTTP_REFERER")
    return flask.redirect(origin_page, 302)


# > EDIT QUOTELIST <
@quotelist_blueprint.route("/edit", methods=["POST"])
def edit_quotelist():
    user = flask_login.current_user
    try:
        user.name
    except AttributeError:
        return flask.redirect("/login")
    
    quotelist_name = flask.request.form.get("quotelist-name")
    quotelist_desc = flask.request.form.get("quotelist-description")
    quotelist_safe_id = flask.request.form.get("quotelist-safe-id")
    
    if len(quotelist_name) < 1:
        flask.flash("[E] Quotelist name is empty")
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page, 302)
    
    quotelist = srp.load(srp.oid_from_safe(quotelist_safe_id))
    
    if quotelist.user != user.name:
        flask.flash("[E] Edit not allowed on others Quotelists")
        origin_page = flask.request.environ.get("HTTP_REFERER")
        return flask.redirect(origin_page, 302)
    
    quotelist.set_name(quotelist_name)
    quotelist.set_description(quotelist_desc)
    
    srp.save(quotelist)
    flask.flash("[S] Quotelist updated")
    
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
        flask.flash("[S] Deleted from Quotelist")
    else:
        quotelist.add_quote_id(quote_safe_id)
        quotelist.srp_save(srp)
        flask.flash("[S] Added to Quotelist")
        
    origin_page = flask.request.environ.get("HTTP_REFERER")
    return flask.redirect(origin_page, 302)