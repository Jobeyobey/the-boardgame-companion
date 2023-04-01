from flask import session, redirect, url_for
from functools import wraps
   
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None:
            return redirect("login")
        return f(*args, **kwargs)
    return decorated_function
