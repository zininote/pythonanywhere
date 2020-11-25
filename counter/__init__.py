from flask import request, make_response
import sqlite3
import datetime as dt

USER = 'zininote'
JS_TEMPLATE = ';var counter = "{:,} / {:,} / {:,}";'

def render():
    # HTTP 리퍼러가 USER 가 아니거나, url 쿼리가 없으면 -1, -1, -1 리턴
    domain = request.referrer or ''
    url = request.args.get('url') or ''
    if USER not in domain or not url:
        res = make_response(JS_TEMPLATE.format(-1, -1, -1), 200)
        res.headers["Content-Type"] = 'text/javascript'
        return res

    # 데이터베이스가 없다면 CREATE
    conn = sqlite3.connect('./data.db')
    conn.execute('PRAGMA journal_mode=WAL')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS counter (url VARCHAR(256) PRIMARY KEY, ycount INTEGER, tcount INTEGER, totalcount INTEGER, udate INTEGER);')

    # 해당 url 데이터베이스 정보 SELECT
    today = dt.datetime.now(tz=dt.timezone(dt.timedelta(hours=9))).toordinal()
    ycount, tcount, totalcount, udate = 0, 0, 0, 0
    c.execute('SELECT * FROM counter WHERE url=?', (url,))
    data = c.fetchone()

    # 추출된 정보가 없다면, url 생성하여 INSERT INTO
    if not data:
        ycount, tcount, totalcount, udate = 0, 1, 1, today
        c.execute('INSERT INTO counter(url, ycount, tcount, totalcount, udate) VALUES(?, ?, ?, ?, ?)', (url, ycount, tcount, totalcount, udate))

    # counts 계산하여 UPDATE
    else:
        _, ycount, tcount, totalcount, udate = tuple(data)
        if today-udate == 1:
            ycount, tcount, udate = tcount, 0, today
        elif today-udate > 1:
            ycount, tcount, udate = 0, 0, today
        tcount += 1
        totalcount += 1
        c.execute('UPDATE counter SET ycount=?, tcount=?, totalcount=?, udate=? WHERE url=?', (ycount, tcount, totalcount, udate, url))

    # 데이터베이스 CLOSE
    conn.commit()
    conn.close()

    # 어제, 오늘, 총 카운터 횟수 리턴
    res = make_response(JS_TEMPLATE.format(ycount, tcount, totalcount), 200)
    res.headers["Content-Type"] = 'text/javascript'
    return res
