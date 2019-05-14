import logging

from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy.orm.exc import NoResultFound

from mantis.model import Corpus, Message, Document, Annotation, User
from mantis.utils import ctx

__all__ = [
    'explorer_page',
]

explorer_page = Blueprint('explorer_page', __name__, template_folder='templates')

logger = logging.getLogger(__name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['txt', 'json']


@explorer_page.route('/', methods=['GET'])
def render_explorer():
    with ctx.SessionContext() as app:
        corpora = app.database.query(Corpus).all()
        html = render_template('pages/explorer.html', messages=app.messages, corpora=corpora, selected_corpus=None)
        app.clear('messages')
        return html


@explorer_page.route('/corpus', methods=['GET'])
def render_explorer_corpus():
    with ctx.SessionContext() as app:
        id_ = request.args.get('id', None, int)
        if id_ is not None:
            corpora = app.database.query(Corpus).all()
            try:
                selected_corpus = app.database.query(Corpus).filter_by(id=id_).one()
                html = render_template(
                    'pages/explorer.html', messages=app.messages, corpora=corpora, selected_corpus=selected_corpus
                )
                app.clear('messages')
                return html
            except NoResultFound as _:
                msg = 'Corpus not found in the database. You will be redirected to a default corpus if exists'
                app.messages.append(Message(Message.Type.ERROR, msg))
        else:
            msg = 'Invalid value for parameter ID. ' \
                  'Found \'{}\' expected an integer'.format(request.args.get('id', None))
            app.messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))


@explorer_page.route('/corpus/add', methods=['POST'])
def render_explorer_corpus_create():
    messages = []
    id_ = request.args.get('id', None, int)
    if id_ is not None:
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                if file and allowed_file(file.filename):
                    with ctx.SessionContext() as app:
                        file_data = file.read().decode('utf-8')  # latin-1
                        for line in file_data.split('\n'):
                            text = line.strip()
                            document = Document(corpus_id=id_, text=text)
                            app.database.add(document)
                        app.database.commit()
                        msg = 'Documents added to Corpus with ID = `{}` successfully'.format(id_)
                        messages.append(Message(Message.Type.SUCCESS, msg))
                else:
                    msg = 'File not allowed in the system'
                    messages.append(Message(Message.Type.ERROR, msg))
            else:
                msg = 'No selected file'
                messages.append(Message(Message.Type.ERROR, msg))
        else:
            msg = 'No file part'
            messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer_corpus', id=id_))
    else:
        msg = 'Invalid value for parameter ID. ' \
              'Found \'{}\' expected an integer'.format(request.args.get('id', None))
        messages.append(Message(Message.Type.ERROR, msg))
    return redirect(url_for('.render_explorer'))


@explorer_page.route('/annotation/create', methods=['POST'])
def render_explorer_annotation_create():
    with ctx.SessionContext() as app:
        id_ = request.form.get('id', None, int)
        if id_ is not None:
            if app.username is not None:
                try:
                    user = app.database.query(User).filter_by(username=app.username).one()
                    # -- construct annotation --
                    owner_id = user.id
                    start = request.form.get('span_start')
                    length = request.form.get('span_length')
                    features = dict(zip(request.form.getlist('feature_key'), request.form.getlist('feature_value')))
                    annotation = Annotation(owner_id=owner_id, document_id=id_, start=start, length=length,
                                            features=features)
                    # -- add to database --
                    app.database.add(annotation)
                    app.database.commit()
                    msg = 'Annotation created successfully'
                    app.messages.append(Message(Message.Type.SUCCESS, msg))
                except NoResultFound as _:
                    msg = 'Invalid username. Your access to this operation has been revoked'
                    app.messages.append(Message(Message.Type.ERROR, msg))
            else:
                msg = 'Login is required to create annotations'
                app.messages.append(Message(Message.Type.ERROR, msg))
            document = app.database.query(Document).get(id_)
            return redirect(url_for('.render_explorer_corpus', id=document.corpus.id))
        else:
            msg = 'Invalid value for the document ID. Found \'{}\' expected an integer'.format(
                request.form.get('id', None)
            )
            app.messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))


@explorer_page.route('/annotation/update', methods=['POST'])
def render_explorer_annotation_update():
    with ctx.SessionContext() as app:
        id_ = request.args.get('id', None, int)
        if id_ is not None:
            if app.username is not None:
                user = None
                try:
                    user = app.database.query(User).filter_by(username=app.username).one()
                except NoResultFound as _:
                    msg = 'Invalid username. Your access to this operation has been revoked'
                    app.messages.append(Message(Message.Type.ERROR, msg))
                if user is not None:
                    owner_id = user.id
                    annotation = app.database.query(Annotation).get(id_)
                    id_ = request.form.get('id', None, int)
                    if owner_id == annotation.owner_id:
                        if id_ == annotation.document.id:
                            start = request.form.get('span_start')
                            length = request.form.get('span_length')
                            features = dict(
                                zip(request.form.getlist('feature_key'), request.form.getlist('feature_value'))
                            )
                            annotation.start = start
                            annotation.length = length
                            annotation.features = features
                            app.database.commit()
                            corpus_id = annotation.document.corpus.id
                            msg = 'Annotation (id=\'{}\') updated successfully'.format(id_)
                            app.messages.append(Message(Message.Type.SUCCESS, msg))
                            return redirect(url_for('.render_explorer_corpus', id=corpus_id))
                        else:
                            msg = 'Can\'t alter the document of the annotation'
                            app.messages.append(Message(Message.Type.ERROR, msg))
                    else:
                        msg = 'You are not authorized to delete annotation with ID \'{}\''.format(id_)
                        app.messages.append(Message(Message.Type.ERROR, msg))
                else:
                    msg = 'Invalid username'
                    app.messages.append(Message(Message.Type.ERROR, msg))
            else:
                msg = 'Login is required to delete annotations'
                app.messages.append(Message(Message.Type.ERROR, msg))
        else:
            msg = 'Invalid value for the document ID. Found \'{}\' expected an integer'.format(
                request.args.get('id', None)
            )
            app.messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))


@explorer_page.route('/annotation/delete', methods=['GET', 'POST'])
def render_explorer_annotation_delete():
    with ctx.SessionContext() as app:
        id_ = request.args.get('id', None, int)
        if id_ is not None:
            if app.username is not None:
                user = None
                try:
                    user = app.database.query(User).filter_by(username=app.username).one()
                except NoResultFound as _:
                    msg = 'Invalid username. Your access to this operation has been revoked'
                    app.messages.append(Message(Message.Type.ERROR, msg))
                if user is not None:
                    owner_id = user.id
                    annotation = app.database.query(Annotation).get(id_)
                    corpus_id = annotation.document.corpus.id
                    if owner_id == annotation.owner_id:
                        app.database.delete(annotation)
                        app.database.commit()
                        msg = 'Annotation (id=\'{}\') deleted successfully'.format(id_)
                        app.messages.append(Message(Message.Type.SUCCESS, msg))
                        return redirect(url_for('.render_explorer_corpus', id=corpus_id))
                    else:
                        msg = 'You are not authorized to delete annotation with ID \'{}\''.format(id_)
                        app.messages.append(Message(Message.Type.ERROR, msg))
                else:
                    msg = 'Invalid username'
                    app.messages.append(Message(Message.Type.ERROR, msg))
            else:
                msg = 'Login is required to delete annotations'
                app.messages.append(Message(Message.Type.ERROR, msg))
        else:
            msg = 'Invalid value for the document ID. Found \'{}\' expected an integer'.format(
                request.args.get('id', None)
            )
            app.messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))
