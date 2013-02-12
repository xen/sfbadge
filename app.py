import os
import datetime
from flask import Flask
from flask import request, redirect
import requests
import simplejson

from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
try:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
except:
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://xen@localhost:5432/heroku"
    app.debug = True

db = SQLAlchemy(app)

@app.route('/')
def hello():
    return redirect('https://github.com/xen/sfbadge')

@app.route('/sf/<project>/json')
def getjson(project):
    today = datetime.date.today()
    weekago = today-datetime.timedelta(days=7)
    payload = {
        'start_date': request.args.get('start_date', weekago.strftime("%Y-%m-%d")), #2013-01-01&
        'end_date': request.args.get('start_date', today.strftime("%Y-%m-%d")),
    }
    r = requests.get('http://sourceforge.net/projects/'+project+'/files/stats/json?', params=payload)
    print r.url
    #import ipdb; ipdb.set_trace()
    #print r.json()
    if request.args.get('jsonp'):
        return """%(jsonp)s({"total": %(total)d})""" % {
            'jsonp': request.args.get('jsonp', 'gettotal'),
            'total': r.json()['total'],
        }
    else:
        return simplejson.dumps({'total': r.json()['total']})


@app.route('/sf/<project>/fulljson')
def getall(project):
    today = datetime.date.today()
    weekago = today-datetime.timedelta(days=7)
    payload = {
        'start_date': request.args.get('start_date', weekago.strftime("%Y-%m-%d")),
        'end_date': request.args.get('start_date', today.strftime("%Y-%m-%d")),
    }
    r = requests.get('http://sourceforge.net/projects/'+project+'/files/stats/json?', params=payload)
    print r.url
    #import ipdb; ipdb.set_trace()
    #print r.json()
    if request.args.get('jsonp'):
        return """%(jsonp)s(%(json)s})""" % {
            'jsonp': request.args.get('jsonp', 'gettotal'),
            'json': simplejson.dumps(r.json()),
        }
    else:
        return r.json()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Git commits stats part

class Commits(db.Model):
    pkid = db.Column(db.Integer, primary_key=True)
    git_user = db.Column(db.String(40))
    git_repo = db.Column(db.String(40))
    forday = db.Column(db.Date)
    count = db.Column(db.Integer)

    def __init__(self, git_user, git_repo, forday, count):
        self.git_user = git_user
        self.git_repo = git_repo
        self.forday = forday
        self.count = count

@app.route('/commits/<git_user>/<git_repo>/json')
def commits(git_user, git_repo):
    WEEK = 7
    MONTH = 31
    data = {
        'commits': sum([x.count for x in db.session.query(Commits).\
                      select_from(Commits).filter(Commits.git_user==git_user).\
                      filter(Commits.git_repo==git_repo).\
                      order_by(Commits.forday.desc()).all()[0:MONTH]
                    ]),
    }

    if request.args.get('jsonp'):
        return """%(jsonp)s(%(data)s)""" % {
            'jsonp': request.args.get('jsonp', 'gettotal'),
            'data': simplejson.dumps(data),
        }
    else:
        return simplejson.dumps(data)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)