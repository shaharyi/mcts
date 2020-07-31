import os

from flask import Flask
from flask import render_template

from flask_bootstrap import Bootstrap
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# Limit request rate per route. Gives client HTTP 429 when exceeded.
limiter = Limiter(key_func=get_remote_address,
                  default_limits=["200 per day", "50 per hour"])


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    bootstrap = Bootstrap(app)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def hello():
        return render_template('index.html')

    from . import tictactoe, ultimate_tictactoe
    app.register_blueprint(tictactoe.bp)
    app.register_blueprint(ultimate_tictactoe.bp)

    return app
