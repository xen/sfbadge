import os
import datetime
from flask import Flask
from flask import request
import requests
import simplejson

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/sf/<project>/n')
def getn(project):
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
        return str(r.json()['total'])

@app.route('/sf/<project>/all')
def getall(project):
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
        return """%(jsonp)s(%(json)s})""" % {
            'jsonp': request.args.get('jsonp', 'gettotal'),
            'json': simplejson.dumps(r.json()),
        }
    else:
        return r.json()

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)