from sqlalchemy.orm.exc import NoResultFound

from mantis.model import User, Message


def check_login(app):
    if app.username is not None:
        try:
            user = app.database.query(User).filter_by(username=app.username).one()
            return user
        except NoResultFound as _:
            msg = 'Sorry, You Are Not Allowed to Access This Page.'
            app.messages.append(Message(Message.Type.ERROR, msg))
    else:
        msg = 'Sorry, You Are Not Allowed to Access This Page.'
        app.messages.append(Message(Message.Type.ERROR, msg))
    return None
