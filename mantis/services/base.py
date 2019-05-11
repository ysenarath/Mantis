import logging

from flask import Blueprint, session as flask_session, jsonify, request
from sqlalchemy.orm.exc import NoResultFound

from mantis.model import Document, User, Annotation
from mantis.utils.db import Session

__all__ = [
    'api',
]

api = Blueprint('web_services', __name__, template_folder='templates')

logger = logging.getLogger(__name__)


@api.route('/document')
def get_document():
    if 'username' not in flask_session:
        return jsonify({'status': 'failed', 'data': 'Authentication required.'})
    username = flask_session['username']
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).one()
    except NoResultFound as _:
        session.close()
        return jsonify({'status': 'failed', 'data': 'You are not authorized for this action.'})
    owner_id = user.id
    id_ = request.args.get('id')
    id_ = int(id_)
    json = {}
    document = session.query(Document).get(id_)
    json['id'] = document.id
    json['corpus_id'] = document.corpus_id
    json['annotations'] = [{
        'id': a.id,
        'span': [a.start, a.start + a.length],
        'owner_id': a.owner_id,
        'features': a.features,
    } for a in document.annotations if owner_id == a.owner_id]
    session.close()
    return jsonify({'status': 'success', 'data': json})


@api.route('/annotation')
def get_annotation():
    if 'username' not in flask_session:
        return jsonify({'status': 'failed', 'data': 'Authentication required.'})
    username = flask_session['username']
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).one()
    except NoResultFound as _:
        session.close()
        return jsonify({'status': 'failed', 'data': 'You are not authorized for this action.'})
    id_ = request.args.get('id')
    id_ = int(id_)
    a = session.query(Annotation).get(id_)
    if a.owner_id != user.id:
        session.close()
        return jsonify({'status': 'failed', 'data': 'You are not authorized for this action.'})
    json = {
        'id': a.id,
        'span': [a.start, a.start + a.length],
        'document_id': a.document_id,
        'owner_id': a.owner_id,
        'features': a.features,
    }
    session.close()
    return jsonify({'status': 'success', 'data': json})
