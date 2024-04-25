import datetime
import math

def time_elapsed(quote_datetime : datetime.datetime):
    time_now = datetime.datetime.now()
    time_elapsed = time_now - quote_datetime
    
    if time_elapsed.days >= 7:
        return f"{math.trunc(time_elapsed.days / 7)} weeks ago"
    elif time_elapsed.days >= 1:
        return f"{time_elapsed.days} days ago"
    elif time_elapsed.seconds >= 3600:
        return f"{math.trunc(time_elapsed.seconds / 3600)}h ago"
    elif time_elapsed.seconds >= 60:
        return f"{math.trunc(time_elapsed.seconds / 60)}min ago"
    elif time_elapsed.seconds > 30:
        return f"{time_elapsed.seconds}s ago"
    else:
        return f"just now"