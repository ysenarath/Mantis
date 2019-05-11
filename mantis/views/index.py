from flask import Blueprint, render_template, abort, session as flask_session, request, url_for, redirect
from jinja2 import TemplateNotFound
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.security import generate_password_hash, check_password_hash

from mantis.model import User, Message
from mantis.utils.db import Session

__all__ = [
    'index_page',
]

index_page = Blueprint('index_page', __name__, template_folder='templates')


@index_page.route('/')
def render_index():
    try:
        username = None
        if 'username' in flask_session:
            username = flask_session['username']
        return render_template('pages/index.html', username=username)
    except TemplateNotFound:
        abort(404)


@index_page.route('/login', methods=['GET', 'POST'])
def render_login():
    try:
        if request.method == 'GET':
            return render_template('pages/login.html')
        else:
            messages = []
            username = request.form['username']
            password = request.form['password']
            session = Session()
            try:
                user = session.query(User).filter_by(username=username).one()
                if not check_password_hash(user.password, password):
                    raise NoResultFound()
                flask_session['username'] = username
            except NoResultFound as _:
                msg = 'Invalid username or password.'
                messages.append(Message(Message.Type.ERROR, msg))
            finally:
                session.close()
            return redirect(url_for('.render_index'))
    except TemplateNotFound:
        abort(404)


@index_page.route('/signup', methods=['GET', 'POST'])
def render_signup():
    if request.method == 'GET':
        return render_template('pages/signup.html')
    else:
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        session = Session()
        session.add(User(username=username, password=password))
        session.commit()
        session.close()
        return redirect(url_for('.render_index'))


@index_page.route('/logout')
def render_logout():
    flask_session['username'] = None
    return redirect(url_for('.render_index'))
