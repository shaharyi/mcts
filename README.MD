# Installation and Set Up
Needs to be tested on AWS ubuntu server free-tier instance.
## Prerequisites:
[For building Python and mod_wsgi from source:]
```
https://medium.com/@garethbjohnson/serve-python-3-7-with-mod-wsgi-on-ubuntu-16-d9c7ab79e03a```
...
Python:
  ./configure --enable-shared
  sudo make; sudo make altinstall
  /sbin/ldconfig -v
mod_wsgi:
  ./configure --with-python=/usr/local/bin/python3.8
  sudo make
  sudo make install
```
* sudo apt update
* [Python 3.6 - usually installed already, test with running python3]
* sudo apt-get install -y python3-venv
* sudo apt-get install -y python3-pip
* sudo apt-get install build-essential libssl-dev libffi-dev python-dev

* sudo apt install virtualenv
 * *On production:*
   * sudo apt install apache2 libapache2-mod-wsgi-py3
   * sudo a2enmod wsgi
   * sudo vi /etc/apache2/sites-enabled/000-default.conf
   
     ```WSGIPassAuthorization ON```
   * sudo apachectl restart
  
Clone the repo from GitHub:
```
git clone https://github.com/shaharyi/mcts
```

Create a virtual environment for the project and activate it:
```
cd myprice
virtualenv -p /usr/bin/python3.6 venv
source venv/bin/activate
```

Install the required packages:
```
pip install -r requirements.txt
```

## Installing D3-Hypertree
https://github.com/glouwa/d3-hypertree
```
$ npm install d3-hypertree --save

$ ln -s ~/node_modules/d3-hypertree/dist flaskr/static/d3-hypertree_dist
```

## Launching the Program
Set the FLASK_APP and FLASK_ENV variables as follows:

* `export FLASK_APP=flaskr`
* `export FLASK_ENV=development`

You can now run the app with the following command: `flask run`

## Built With...
* [Flask](http://flask.pocoo.org/)

## Credits and License

Copyright (c) 2020 [Shahar Yifrah](https://github.com/shaharyi)

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
