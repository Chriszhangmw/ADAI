from flask import Flask
from flask_sqlalchemy import SQLAlchemy


from config import config


db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    from .main import main as main_blueprint
    from .main.ars_route import ars_route
    from .main.query import query
    app.register_blueprint(main_blueprint)
    app.register_blueprint(ars_route, url_prefix='/ars')
    app.register_blueprint(query, url_prefix='/query')
    return app
