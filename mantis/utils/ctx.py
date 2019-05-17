from contextlib import ContextDecorator

from flask import session as flask_session

from mantis.utils import db


class SessionContext(ContextDecorator):
    def __enter__(self):
        if 'messages' not in flask_session:
            flask_session['messages'] = []
        self.database = db.Session()
        return self

    def __exit__(self, *exc):
        self.database.close()
        return 0

    def __getattr__(self, item):
        if item in flask_session:
            return flask_session[item]
        else:
            return None

    def __setattr__(self, key, value):
        if key != 'database':
            flask_session[key] = value
        else:
            self.__dict__['database'] = value

    # noinspection PyMethodMayBeStatic
    def clear(self, *keys):
        for key in keys:
            if key in flask_session and isinstance(flask_session[key], list):
                flask_session[key] = []
            else:
                flask_session[key] = None
