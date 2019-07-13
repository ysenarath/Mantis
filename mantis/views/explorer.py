import logging

from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy.orm.exc import NoResultFound

from mantis.model import Corpus, Message, Document, Annotation, Pagination, serialize
from mantis.utils import ctx
from mantis.views.login import check_login

__all__ = [
    'page',
]

page = Blueprint('explorer_page', __name__, template_folder='templates')

logger = logging.getLogger(__name__)


@page.route('/', methods=['GET'])
def render_explorer():
    with ctx.SessionContext() as app:
        user = check_login(app)
        if user:
            corpora = app.database.query(Corpus).all()
            html = render_template('pages/explorer.html', messages=app.messages, corpora=corpora, selected_corpus=None)
            app.clear('messages')
        else:
            html = redirect(url_for('index_page.render_index'))
        return html


def serialize_documents(documents):
    return {'documents': [{**item.serialize(), 'annotations': serialize(item.annotations)} for item in documents]}


@page.route('/corpus', methods=['GET'])
def render_explorer_corpus():
    with ctx.SessionContext() as app:
        user = check_login(app)
        if user:
            id_ = request.args.get('id', None, int)
            index = request.args.get('page', 1, int)
            if id_ is not None:
                corpora = app.database.query(Corpus).all()
                try:
                    sel_corpus = app.database.query(Corpus).filter_by(id=id_).one()
                except NoResultFound as _:
                    msg = 'Corpus not found in the database. You will be redirected to a default corpus if exists'
                    app.messages.append(Message(Message.Type.ERROR, msg))
                else:
                    qry_documents = app.database.query(Document).filter_by(corpus_id=id_)
                    pagination = Pagination(qry_documents)
                    page_ = pagination.get(index)
                    sel_corpus = {**sel_corpus.serialize(), **serialize_documents(page_.items)}
                    html = render_template(
                        'pages/explorer.html',
                        messages=app.messages, corpora=corpora, selected_corpus=sel_corpus, pagination=pagination,
                        page=page_
                    )
                    app.clear('messages')
                    return html
            else:
                msg = 'Invalid value for parameter ID. ' \
                      'Found \'{}\' expected an integer'.format(request.args.get('id', None))
                app.messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))


@page.route('/annotation/create', methods=['POST'])
def render_explorer_annotation_create():
    with ctx.SessionContext() as app:
        user = check_login(app)
        if user:
            id_ = request.form.get('id', None, int)
            if id_ is not None:
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
                document = app.database.query(Document).get(id_)
                return redirect(url_for('.render_explorer_corpus', id=document.corpus.id))
            else:
                msg = 'Invalid value for the document ID. Found \'{}\' expected an integer'.format(
                    request.form.get('id', None)
                )
                app.messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))


@page.route('/annotation/update', methods=['POST'])
def render_explorer_annotation_update():
    with ctx.SessionContext() as app:
        user = check_login(app)
        if user:
            id_ = request.args.get('id', None, int)
            if id_ is not None:
                owner_id = user.id
                annotation = app.database.query(Annotation).get(id_)
                id_ = request.form.get('id', None, int)
                if owner_id == annotation.owner_id:
                    if id_ == annotation.document.id:
                        start = request.form.get('span_start')
                        length = request.form.get('span_length')
                        feature_keys = request.form.getlist('feature_key')
                        feature_values = request.form.getlist('feature_value')
                        features = dict(zip(feature_keys, feature_values))
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
                msg = 'Invalid value for the document ID. Found \'{}\' expected an integer'.format(
                    request.args.get('id', None)
                )
                app.messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))


@page.route('/annotation/delete', methods=['GET', 'POST'])
def render_explorer_annotation_delete():
    with ctx.SessionContext() as app:
        user = check_login(app)
        if user:
            id_ = request.args.get('id', None, int)
            if id_ is not None:
                owner_id = user.id
                annotation = app.database.query(Annotation).get(id_)
                if annotation is not None:
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
                    msg = 'Unable to find an annotation with the provided ID \'{}\''.format(id_)
                    app.messages.append(Message(Message.Type.ERROR, msg))
            else:
                msg = 'Invalid value for the document ID. Found \'{}\' expected an integer'.format(
                    request.args.get('id', None)
                )
                app.messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_explorer'))
