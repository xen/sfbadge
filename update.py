import os
import requests
from requests.auth import HTTPBasicAuth
import psycopg2
import urlparse
import datetime

def unparse(url):
    urlparse.uses_netloc.append('postgres')
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    return "dbname=%s user=%s password=%s host=%s " % \
        (url.path[1:], url.username, url.password, url.hostname)

try:
    db_url = unparse(os.environ['DATABASE_URL'])
except:
    db_url = "user=xen host=localhost dbname=heroku port=5432"

conn = psycopg2.connect(db_url)
cur = conn.cursor()

for_update = "SELECT pkid, git_user, git_repo, last_update, first_time FROM updates;"
cur.execute(for_update)
result = cur.fetchall()

def update(git_user, git_repo, date_since, date_until):
    r = requests.get("https://api.github.com/repos/%(git_user)s/%(git_repo)s/commits?since=%(date_since)s&until=%(date_until)s&per_page=100" % {
            'git_user': git_user,
            'git_repo': git_repo,
            'date_since': date_since.strftime("%Y-%m-%d"),
            'date_until': date_until.strftime("%Y-%m-%d"),
        }, auth=HTTPBasicAuth('sfbadge', '1234qwer'))
    print(r.url)

    cur.execute("DELETE FROM commits WHERE git_user=%(git_user)s AND git_repo=%(git_repo)s AND forday=%(forday)s;", {
            'git_user': git_user,
            'git_repo': git_repo,
            'forday': date_until,
        })

    cur.execute("INSERT INTO commits(git_user, git_repo, forday, count) VALUES (%(git_user)s, %(git_repo)s, %(forday)s, %(count)s);", {
            'git_user': git_user,
            'git_repo': git_repo,
            'forday': date_until,
            'count': len(r.json()),
        })
    return len(r.json())

WEEK = 7

for (pkid, git_user, git_repo, last_update, first_time) in result:
    base = datetime.datetime.today()
    if first_time:
        print([ update(git_user, git_repo, base - datetime.timedelta(days=x+1),
            base - datetime.timedelta(days=x)) for x in range(0,WEEK) ])
        cur.execute("UPDATE updates SET first_time=FALSE WHERE pkid = %(pkid)s", {'pkid':pkid})
    else:
        print(update(git_user, git_repo, base - datetime.timedelta(days=1), base))

conn.commit()
cur.close()
conn.close()