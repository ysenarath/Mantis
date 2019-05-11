import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, Session as _Session_

from mantis.model import Model


class _Session(_Session_):
    def __init__(self, **kwargs):
        super(_Session, self).__init__(**kwargs)

    def get_or_create(self, model, **kwargs):
        instance = self.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            self.add(instance)
            self.commit()
            return instance


Session = sessionmaker(class_=_Session)


def create_engine(uri):
    return db.create_engine('{}?charset=utf8mb4'.format(uri))


def bind_engine(bind):
    Model.metadata.bind = bind
    Session.configure(bind=bind)
    return Session
