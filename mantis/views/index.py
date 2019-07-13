from flask import Blueprint, render_template, request, url_for, redirect
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.security import generate_password_hash, check_password_hash

from mantis.model import User, Message
from mantis.utils import ctx

__all__ = [
    'page',
]

page = Blueprint('index_page', __name__, template_folder='templates')


@page.app_context_processor
def inject_user():
    with ctx.SessionContext() as app:
        try:
            user = app.database.query(User).filter_by(username=app.username).one()
        except NoResultFound as _:
            user = None
        return dict(user=user)


@page.route('/')
def render_index():
    with ctx.SessionContext() as app:
        html = render_template('pages/index.html', messages=app.messages)
        app.clear('messages')
        return html


@page.route('/login', methods=['GET', 'POST'])
def render_login():
    with ctx.SessionContext() as app:
        if request.method == 'GET':
            return render_template('pages/login.html')
        else:
            messages = []
            username = request.form['username']
            password = request.form['password']
            try:
                user = app.database.query(User).filter_by(username=username).one()
                if not check_password_hash(user.password, password):
                    raise NoResultFound()
            except NoResultFound as _:
                msg = 'Invalid username or password.'
                messages.append(Message(Message.Type.ERROR, msg))
            else:
                app.username = username
            return redirect(url_for('.render_index'))


@page.route('/signup', methods=['GET', 'POST'])
def render_signup():
    with ctx.SessionContext() as app:
        if request.method == 'GET':
            return render_template('pages/signup.html')
        else:
            username = request.form['username']
            password = generate_password_hash(request.form['password'])
            app.database.add(User(username=username, password=password))
            app.database.commit()
            return redirect(url_for('.render_index'))


@page.route('/logout')
def render_logout():
    with ctx.SessionContext() as app:
        app.username = None
        return redirect(url_for('.render_index'))
