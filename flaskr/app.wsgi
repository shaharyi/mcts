# put this file under /var/www/wsgi-scripts

python_home = '/var/www/mcts/py37-venv'

import sys
import site

# Calculate path to site-packages directory.

python_version = '.'.join(map(str, sys.version_info[:2]))
site_packages = python_home + '/lib/python%s/site-packages' % python_version

# Add the site-packages directory.

site.addsitedir(site_packages)


import os
import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/mcts/")

os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_APP'] = 'run.py'

from flaskr import create_app
application = create_app()
