import functools # The functools module in Python deals with higher-order functions, simple terms they are functions which take other functions as arguments. The primary object that the functools module deals with is the decorator, which is a function that wraps another function or method. The primary purpose of decorators is to modify or extend the behavior of functions or methods. The functools module provides several functions that can be used to create decorators. The module also provides a few other higher-order functions, which are used to manipulate or create other functions.
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash 
from document_analysis.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth') # Create a Blueprint named 'auth' with the name of the current module (__name__) and the URL prefix '/auth'.

def login_required(view):
    """It's a decorator that will redirect to the login page if the user is not logged in.

    Args:
        view (function): The view function to be decorated.

    Returns:
        function: The wrapped view function that includes the login check.
    """
    @functools.wraps(view) # The functools.wraps() function is a decorator that takes a function used in a decorator and adds the functionality of copying over the function name, docstring, arguments list, etc. This allows you to wrap a function in a decorator without losing the information of the original function.
    def wrapped_view(**kwargs):
        if g.user is None: # g is a special object that is unique for each request. It is used to store data that might be accessed by multiple functions during the request. The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request.
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.before_app_request # Register a function that runs before the view function, no matter what URL is requested. This is used to load a user from the session.
def load_logged_in_user(): 
    """It's a function that loads the logged in user from the session.
    """
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/register', methods=('GET', 'POST')) # Register a new view function for the '/register' URL that accepts both GET and POST requests.
def register():
    """It's a view function that registers a new user.

    Returns:
        str: It returns the rendered template of the register.html file.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f'User {username} is already registered.'

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)
        
    # If the request method is GET or the data is invalid, the register page should be shown.
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST')) # Register a new view function for the '/login' URL that accepts both GET and POST requests.
def login():
    """It's a view function that logs in a user.

    Returns:
        str: It returns the rendered template of the login.html file.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)
        
    # If the request method is GET or the data is invalid, the login page should be shown.
    return render_template('auth/login.html')

@bp.route('/logout') # Register a new view function for the '/logout' URL.
def logout():
    """It's a view function that logs out a user.

    Returns:
        str: It redirects the user to the index page.
    """
    session.clear()
    return redirect(url_for('index'))