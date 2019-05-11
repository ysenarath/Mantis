import logging

from flask import Blueprint, render_template, abort, redirect, url_for, request
from jinja2 import TemplateNotFound
from sqlalchemy.exc import SQLAlchemyError

from mantis.model import Corpus, Message
from mantis.utils import db

__all__ = [
    'corpus_page',
]

corpus_page = Blueprint('corpus_page', __name__, template_folder='templates')

logger = logging.getLogger(__name__)


@corpus_page.route('/', methods=['GET'])
def render_corpus():
    session = db.Session()
    try:
        messages = []
        corpora = session.query(Corpus).all()
        html = render_template('pages/corpus.html', messages=messages, corpora=corpora, mode='view')
        return html
    except TemplateNotFound:
        abort(404)
    finally:
        session.close()


@corpus_page.route('/create', methods=['POST'])
def render_corpus_add():
    session = db.Session()
    try:
        messages = []
        corpus = Corpus(name=request.form['corpus_name'])
        try:
            session.add(corpus)
            session.commit()
            messages += [Message(Message.Type.SUCCESS, 'Corpus created successfully.')]
        except SQLAlchemyError as err:
            logger.info('Failed Operation: {}'.format(err))
            messages += [Message(Message.Type.ERROR, 'SQL Error. Please contact admin for further assistance.')]
        return redirect(url_for('.render_corpus'))
    except TemplateNotFound:
        abort(404)
    finally:
        session.close()


@corpus_page.route('/delete', methods=['GET'])
def render_corpus_delete():
    messages = []
    if 'id' not in request.args:
        msg = 'Identity of the corpus not found!'
        messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_corpus'))
    id_ = request.args.get('id')
    try:
        id_ = int(id_)
    except ValueError as _:
        msg = 'Invalid type for ID parameter. Expected {} found {}.'.format(type(0), type(id_))
        messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_corpus'))
    session = db.Session()
    try:
        corpus = session.query(Corpus).get(id_)
        if corpus is not None:
            session.delete(corpus)
            session.commit()
            messages += [Message(Message.Type.SUCCESS, 'Corpus with ID `{}` deleted successfully.'.format(id_))]
        else:
            messages += [Message(Message.Type.ERROR, 'No such corpus with ID `{}` to delete.'.format(id_))]
        return redirect(url_for('.render_corpus'))
    except TemplateNotFound:
        abort(404)
    finally:
        session.close()


@corpus_page.route('/edit', methods=['GET', 'POST'])
def render_corpus_edit():
    session = db.Session()
    try:
        messages = []
        id_ = int(request.args.get('id'))
        if request.method == 'POST':
            corpus = session.query(Corpus).get(id_)
            if corpus is not None:
                corpus.name = request.form['corpus_name']
                session.commit()
                messages += [Message(Message.Type.SUCCESS, 'Corpus with ID `{}` deleted successfully.'.format(id_))]
            else:
                messages += [Message(Message.Type.ERROR, 'No such corpus with ID `{}` to delete.'.format(id_))]
            return redirect(url_for('.render_corpus'))
        else:
            corpora = session.query(Corpus).all()
            html = render_template('pages/corpus.html', messages=messages, corpora=corpora, mode='edit', edit_id=id_)
            return html
    except TemplateNotFound:
        abort(404)
    finally:
        session.close()
