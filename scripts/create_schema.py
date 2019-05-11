from mantis.model import Model
from mantis.utils import config, db

if __name__ == '__main__':
    config = config.Config()
    engine = db.create_engine(config.database['url'])
    db.bind_engine(bind=engine)
    Model.metadata.create_all(engine)
