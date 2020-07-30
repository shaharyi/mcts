import os
from importlib import import_module
from . import create_app

config_name = os.getenv('FLASK_ENV')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
