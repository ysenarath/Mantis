import os
from datetime import timedelta

from flask import Flask, url_for
from flask_session import Session

from mantis.services import api
from mantis.utils import config, db
from mantis.views import *

config = config.Config('config.ini')

TEMP_DIR = 'data/temp'


def build_app():
    flask_app = Flask(__name__)

    flask_app.config['SESSION_PERMANENT'] = True
    flask_app.config['SESSION_TYPE'] = 'filesystem'
    flask_app.config['SESSION_FILE_DIR'] = TEMP_DIR + '/flask_sessions'
    flask_app.config['SECRET_KEY'] = 'Ty%EC!ndi^MAnI)Th3H0L3'
    flask_app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)

    flask_session = Session()
    flask_session.init_app(flask_app)

    engine = db.create_engine(config.database['url'])
    db.bind_engine(bind=engine)

    flask_app.register_blueprint(index_page)

    flask_app.register_blueprint(explorer_page, url_prefix='/explorer')

    flask_app.register_blueprint(corpus_page, url_prefix='/corpus')

    flask_app.register_blueprint(api, url_prefix='/api')

    return flask_app


app = build_app()


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


if __name__ == '__main__':
    app.run(debug=True)
