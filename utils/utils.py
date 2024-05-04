import datetime
import math

def time_elapsed(quote_datetime : datetime.datetime):
    time_now = datetime.datetime.now()
    time_elapsed = time_now - quote_datetime
    
    if time_elapsed.days >= 7:
        return f"{math.trunc(time_elapsed.days / 7)}w ago"
    elif time_elapsed.days >= 1:
        return f"{time_elapsed.days}d ago"
    elif time_elapsed.seconds >= 3600:
        return f"{math.trunc(time_elapsed.seconds / 3600)}h ago"
    elif time_elapsed.seconds >= 60:
        return f"{math.trunc(time_elapsed.seconds / 60)}min ago"
    elif time_elapsed.seconds > 30:
        return f"{time_elapsed.seconds}s ago"
    else:
        return f"just now"
    
def set_quotes_quotelists(quotes, quotelists, srp):
    """Add to each quote the quotelists available to be added or removed from."""
    
    for quote in quotes:
        quote.safe_id = quote.get_safe_id(srp) 
        quote.quotelists_names = []
        for quotelist in quotelists:
            if quote.safe_id in quotelist.quote_ids:
                name = f"✓ {quotelist.name}"
                quote.quotelists_names.append(name)
            else:
                quote.quotelists_names.append(quotelist.name)
        #Quote time elapsed since publication
        quote.time_elapsed = time_elapsed(quote.date)
    return quotes