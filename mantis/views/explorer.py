import logging

from flask import Blueprint, render_template, abort, request, redirect, url_for, session as flask_session
from jinja2 import TemplateNotFound
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from werkzeug.utils import secure_filename

from mantis.model import Corpus, Message, Document, Annotation, User
from mantis.utils import db
from mantis.utils.db import Session

__all__ = [
    'explorer_page',
]

explorer_page = Blueprint('explorer_page', __name__, template_folder='templates')

logger = logging.getLogger(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['txt', 'json']


@explorer_page.route('/', methods=['GET'])
def render_explorer():
    messages = []
    session = db.Session()
    corpora = session.query(Corpus).all()
    if len(corpora) == 0:
        msg = 'Please contact developer. The database contains more than one corpus with provided id.'
        messages.append(Message(Message.Type.ERROR, msg))
    try:
        html = render_template('pages/explorer.html', messages=messages, corpora=corpora, selected_corpus=None)
        return html
    except TemplateNotFound:
        abort(404)
    finally:
        session.close()


@explorer_page.route('/corpus', methods=['GET'])
def render_explorer_corpus():
    messages = []
    session = db.Session()
    corpora = session.query(Corpus).all()
    selected_corpus = None
    if len(corpora) == 0:
        return redirect(url_for('.render_explorer'))
    if 'id' in request.args:
        id_ = request.args.get('id')
        try:
            id_ = int(id_)
            try:
                selected_corpus = session.query(Corpus).filter_by(id=id_).one()
            except MultipleResultsFound as _:
                msg = 'Please contact developer. The database contains more than one corpus with provided id.'
                messages.append(Message(Message.Type.ERROR, msg))
            except NoResultFound as _:
                msg = 'Corpus not found in the database. You will be redirected to a default corpus if exists.'
                messages.append(Message(Message.Type.ERROR, msg))
        except ValueError as _:
            msg = 'Invalid type for ID parameter. Expected {} found {}.'.format(type(0), type(id_))
            messages.append(Message(Message.Type.ERROR, msg))
    else:
        msg = 'Identity of the corpus not found!'
        messages.append(Message(Message.Type.ERROR, msg))
    if selected_corpus is None and len(corpora) > 0:
        selected_corpus = corpora[0]
        session.close()
        return redirect(url_for('.render_explorer_corpus', id=selected_corpus.id))
    try:
        html = render_template(
            'pages/explorer.html', messages=messages, corpora=corpora, selected_corpus=selected_corpus
        )
        return html
    except TemplateNotFound:
        abort(404)
    finally:
        session.close()


@explorer_page.route('/corpus/create', methods=['POST'])
def render_explorer_corpus_create():
    messages = []
    if 'id' not in request.args:
        msg = 'Identity of the corpus not found.'
        messages.append(Message(Message.Type.ERROR, msg))
        logger.debug('File upload failed: {}'.format(msg))
        return redirect(url_for('.render_explorer'))
    id_ = request.args.get('id')
    if 'file' not in request.files:
        msg = 'No file part'
        messages.append(Message(Message.Type.ERROR, msg))
        logger.debug('File upload failed: {}'.format(msg))
        return redirect(url_for('.render_explorer_corpus', id=id_))
    file = request.files['file']
    if file.filename == '':
        msg = 'No selected file'
        messages.append(Message(Message.Type.ERROR, msg))
        logger.debug('File upload failed: {}'.format(msg))
        return redirect(url_for('.render_explorer_corpus', id=id_))
    try:
        id_ = int(id_)
    except ValueError as _:
        msg = 'Invalid type for ID parameter. Expected {} found {}.'.format(type(0), type(id_))
        messages.append(Message(Message.Type.ERROR, msg))
        logger.debug('File upload failed: {}'.format(msg))
        return redirect(url_for('.render_explorer'))
    if file and allowed_file(file.filename):
        session = db.Session()
        filename = secure_filename(file.filename)
        print('Uploading file with name`{}`'.format(filename))
        file_data = file.read().decode('utf-8')  # latin-1
        for line in file_data.split('\n'):
            text = line.strip()
            document = Document(corpus_id=id_, text=text)
            session.add(document)
        session.commit()
        session.close()
        msg = 'Documents added to Corpus with ID = `{}` successfully.'.format(id_)
        messages.append(Message(Message.Type.SUCCESS, msg))
        logger.debug('File upload success: {}'.format(msg))
        return redirect(url_for('.render_explorer_corpus', id=id_))
    else:
        msg = 'File not allowed in the system.'
        messages.append(Message(Message.Type.ERROR, msg))
        logger.debug('File upload failed: {}'.format(msg))
        return redirect(url_for('.render_explorer_corpus', id=id_))


@explorer_page.route('/annotation/create', methods=['POST'])
def render_explorer_annotation_create():
    messages = []
    session = Session()
    if 'username' not in flask_session:
        msg = 'You have to login to create annotations.'
        messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))
    try:
        username = flask_session['username']
        user = session.query(User).filter_by(username=username).one()
        owner_id = user.id
        id_ = request.form.get('id')
        start = request.form.get('span_start')
        length = request.form.get('span_length')
        features = dict(zip(request.form.getlist('feature_key'), request.form.getlist('feature_value')))
        annotation = Annotation(owner_id=owner_id, document_id=id_, start=start, length=length, features=features)
        session.add(annotation)
        session.commit()
        document = session.query(Document).get(id_)
        return redirect(url_for('.render_explorer_corpus', id=document.corpus.id))
    except NoResultFound as _:
        msg = 'Invalid username. Your access to this operation has been revoked.'
        messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))
    finally:
        session.close()


@explorer_page.route('/annotation/update', methods=['POST'])
def render_explorer_annotation_update():
    messages = []
    session = Session()
    if 'username' not in flask_session:
        msg = 'You have to login to create annotations.'
        messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))
    try:
        username = flask_session['username']
        user = session.query(User).filter_by(username=username).one()
        owner_id = user.id
        id_ = request.form.get('id')
        start = request.form.get('span_start')
        length = request.form.get('span_length')
        features = dict(zip(request.form.getlist('feature_key'), request.form.getlist('feature_value')))
        annotation = Annotation(owner_id=owner_id, document_id=id_, start=start, length=length, features=features)
        session.add(annotation)
        session.commit()
        document = session.query(Document).get(id_)
        return redirect(url_for('.render_explorer_corpus', id=document.corpus.id))
    except NoResultFound as _:
        msg = 'Invalid username. Your access to this operation has been revoked.'
        messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))
    finally:
        session.close()


@explorer_page.route('/annotation/delete', methods=['GET'])
def render_explorer_annotation_delete():
    messages = []
    session = Session()
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
    if 'username' not in flask_session:
        msg = 'You have to login to create annotations.'
        messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))
    try:
        username = flask_session['username']
        user = session.query(User).filter_by(username=username).one()
        owner_id = user.id
        annotation = session.query(Annotation).get(id_).one()
        if owner_id != annotation.owner_id:
            raise NoResultFound()
        session.commit()
        return redirect(url_for('.render_explorer_corpus', id=annotation.document.corpus.id))
    except NoResultFound as _:
        msg = 'Invalid username. Your access to this operation has been revoked.'
        messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))
    finally:
        session.close()
