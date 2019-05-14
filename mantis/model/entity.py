from six import string_types
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Model = declarative_base()


def serialize(e):
    if isinstance(e, (int, float, bool)) or isinstance(e, string_types):
        return e
    if isinstance(e, list):
        return [serialize(v) for v in e]
    if isinstance(e, dict):
        return {k: serialize(v) for k, v in e.items()}
    if isinstance(e, set):
        return serialize(list(e))
    if hasattr(e, 'serialize'):
        return e.serialize()
    return None


class User(Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(256), unique=True, nullable=False)
    password = Column(String(512), nullable=False)


class Corpus(Model):
    __tablename__ = 'corpus'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True, nullable=False)
    documents = relationship('Document', back_populates='corpus', cascade='all, delete-orphan')

    def serialize(self):
        # noinspection PyTypeChecker
        return {'id': self.id, 'name': self.name, 'documents': [serialize(d) for d in self.documents]}


class Document(Model):
    __tablename__ = 'document'
    id = Column(Integer, primary_key=True)
    corpus_id = Column(Integer, ForeignKey('corpus.id'))
    corpus = relationship(Corpus, back_populates='documents')
    text = Column(Text, nullable=False)
    annotations = relationship('Annotation', back_populates='document', cascade='all, delete-orphan')

    def serialize(self):
        # noinspection PyTypeChecker
        return {
            'id': self.id, 'corpus_id': self.corpus_id, 'text': self.text,
            'annotations': [serialize(a) for a in self.annotations]
        }


class Annotation(Model):
    __tablename__ = 'annotation'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    document_id = Column(Integer, ForeignKey('document.id'))
    document = relationship('Document', back_populates='annotations')
    start = Column(Integer)
    length = Column(Integer)
    features = Column(JSON)

    def serialize(self):
        # noinspection PyTypeChecker
        return {
            'id': self.id, 'owner_id': self.owner_id, 'document_id': self.document_id,
            'start': self.start, 'length': self.length, 'features': self.features
        }
