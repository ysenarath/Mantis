from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Model = declarative_base()


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


class Document(Model):
    __tablename__ = 'document'
    id = Column(Integer, primary_key=True)
    corpus_id = Column(Integer, ForeignKey('corpus.id'))
    corpus = relationship(Corpus, back_populates='documents')
    text = Column(Text, nullable=False)
    annotations = relationship('Annotation', back_populates='document')


class Annotation(Model):
    __tablename__ = 'annotation'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    document_id = Column(Integer, ForeignKey('document.id'), nullable=False)
    document = relationship('Document', back_populates='annotations')
    start = Column(Integer)
    length = Column(Integer)
    features = Column(JSON)
