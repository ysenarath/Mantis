import logging

from flask import Blueprint, render_template, redirect, url_for, request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from mantis.model import Corpus, Message, Document, serialize
from mantis.utils import ctx

__all__ = [
    'page',
]

page = Blueprint('corpus_page', __name__, template_folder='templates')

logger = logging.getLogger(__name__)


def serialize_corpora(e):
    corpora = serialize(e.database.query(Corpus).all())
    for corpus in corpora:
        corpus['documents'] = {
            'length': e.database.query(Document).filter_by(corpus_id=corpus['id']).count()
        }
    return corpora


@page.route('/', methods=['GET'])
def render_corpus():
    with ctx.SessionContext() as app:
        corpora = serialize_corpora(app)
        html = render_template('pages/corpus.html', messages=app.messages, corpora=corpora, mode='view')
        app.clear('messages')
        return html


@page.route('/create', methods=['POST'])
def render_corpus_add():
    with ctx.SessionContext() as app:
        corpus = Corpus(name=request.form['corpus_name'])
        try:
            app.database.add(corpus)
            app.database.commit()
            app.messages.append(Message(Message.Type.SUCCESS, 'Corpus created successfully'))
        except IntegrityError as err:
            app.database.rollback()
            if "Duplicate entry '{}' for key 'name'".format(corpus.name) in str(err):
                msg = 'Corpus name already exists \'{}\''.format(corpus.name)
                app.messages.append(Message(Message.Type.ERROR, msg))
            else:
                msg = 'Please contact admin for further assistance'
                app.messages.append(Message(Message.Type.ERROR, msg))
        except SQLAlchemyError as _:
            msg = 'Please contact admin for further assistance'
            app.messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_corpus'))


@page.route('/delete', methods=['GET'])
def render_corpus_delete():
    id_ = request.args.get('id', None, int)
    with ctx.SessionContext() as app:
        if id_ is not None:
            corpus = app.database.query(Corpus).get(id_)
            if corpus is not None:
                app.database.delete(corpus)
                app.database.commit()
                msg = 'Corpus with ID \'{}\' deleted successfully.'.format(id_)
                app.messages.append(Message(Message.Type.SUCCESS, msg))
            else:
                msg = 'No such corpus with ID \'{}\' to delete.'.format(id_)
                app.messages.append(Message(Message.Type.ERROR, msg))
        else:
            msg = 'Invalid value for parameter ID. Found \'{}\' expected an integer.'.format(id_)
            app.messages.append(Message(Message.Type.ERROR, msg))
    return redirect(url_for('.render_corpus'))


@page.route('/edit', methods=['GET', 'POST'])
def render_corpus_edit():
    with ctx.SessionContext() as app:
        id_ = request.args.get('id', None, int)
        if id_ is not None:
            if request.method == 'POST':
                corpus = app.database.query(Corpus).get(id_)
                if corpus is not None:
                    corpus.name = request.form['corpus_name']
                    app.database.commit()
                    msg = 'Corpus with ID \'{}\' deleted successfully.'.format(id_)
                    app.messages.append(Message(Message.Type.SUCCESS, msg))
                else:
                    msg = 'No such corpus with ID \'{}\' to delete.'.format(id_)
                    app.messages.append(Message(Message.Type.ERROR, msg))
            else:
                corpora = serialize_corpora(app)
                html = render_template(
                    'pages/corpus.html', messages=app.messages, corpora=corpora, mode='edit', edit_id=id_
                )
                app.clear('messages')
                return html
        else:
            msg = 'Invalid value for parameter ID. Found \'{}\' expected an integer.'.format(id_)
            app.messages.append(Message(Message.Type.ERROR, msg))
        return redirect(url_for('.render_corpus'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['txt', 'json']


@page.route('/add', methods=['POST'])
def render_corpus_document_add():
    with ctx.SessionContext() as app:
        id_ = request.args.get('id', None, int)
        if id_ is not None:
            if 'file' in request.files:
                file = request.files['file']
                if file.filename != '':
                    if file and allowed_file(file.filename):
                        file_data = file.read().decode('utf-8')  # latin-1
                        for line in file_data.split('\n'):
                            text = line.strip()
                            document = Document(corpus_id=id_, text=text)
                            app.database.add(document)
                        app.database.commit()
                        msg = 'Documents added to Corpus with ID = `{}` successfully'.format(id_)
                        app.messages.append(Message(Message.Type.SUCCESS, msg))
                    else:
                        msg = 'File not allowed in the system'
                        app.messages.append(Message(Message.Type.ERROR, msg))
                else:
                    msg = 'No selected file'
                    app.messages.append(Message(Message.Type.ERROR, msg))
            else:
                msg = 'No file part'
                app.messages.append(Message(Message.Type.ERROR, msg))
        else:
            msg = 'Invalid value for parameter ID. ' \
                  'Found \'{}\' expected an integer'.format(request.args.get('id', None))
            app.messages.append(Message(Message.Type.ERROR, msg))
    return redirect(url_for('.render_corpus'))
