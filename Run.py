import logging
import random
import sqlite3
from string import ascii_letters, digits

import requests
from flask import Flask, abort, redirect, render_template, request, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask('', template_folder='', static_folder='')
limiter = Limiter(key_func = get_remote_address, app = app, storage_uri='memory://')
logging.basicConfig(level=logging.DEBUG, filename='log.log', filemode='a', format='%(asctime)s %(levelname)s: %(message)s')
database = sqlite3.connect('Database.db')

def PrintLogMsg(msg: str) -> None:
    logging.info(msg)
    print(msg)

PrintLogMsg("Successfully connected to the database")

def read_database() -> None:
    global data
    c = database.cursor()
    try:
        data = dict(c.execute("SELECT id, url from URL"))
        database.commit()
        logging.info("Successfully read the database")
    except sqlite3.OperationalError:
        c.execute('''CREATE TABLE URL(
                 ID  TEXT PRIMARY KEY     NOT NULL,
                 URL TEXT                 NOT NULL);''')
        logging.info("Successfully created the table")
        read_database()

def write_database(url: str) -> str:
    global data
    c = database.cursor()
    while True:
        try:
            id = ''.join(random.sample(digits + ascii_letters, 5))
            c.execute("INSERT INTO URL (ID,URL) VALUES " + f"('{id}', '{url}')")
            data = c.execute("SELECT id, url from URL")
            database.commit()
            return id
        except: ...

def search_id(url: str) -> str | bool:
    c = database.cursor()
    data = c.execute(f'select id from URL where url="{url}"')
    for i in data:
        return i[0]
    else:
        return False

def search_url(id: str) -> str | bool:
    c = database.cursor()
    data = c.execute(f'select url from URL where ID="{id}"')
    for i in data:
        return i[0]
    else:
        return False

@app.errorhandler(400)
def Error_400(e):
    return render_template('html/Error.html', code='400', reason='Bad Request', title='錯誤請求'), 400

@app.errorhandler(403)
def Error_403(e):
    return render_template('html/Error.html', code='403', reason='Forbidden', title='拒絕訪問'), 403

@app.errorhandler(404)
def Error_404(e):
    return render_template('html/Error.html', code='404', reason='Page Not Found', title='找不到頁面'), 404

@app.errorhandler(429)
def Error_429(e):
    return render_template('html/Error.html', code='429', reason='Too Many Requests', title='請求次數過多'), 429

@app.errorhandler(500)
def Error_500(e):
    return render_template('html/Error.html', code='500', reason='Internal Server Error', title='伺服器錯誤'), 500

@app.after_request
def after_request(response):
    environ = request.environ
    res = f"{environ.get('REMOTE_ADDR')} - - \"{environ.get('REQUEST_METHOD')} {environ.get('PATH_INFO')} {environ.get('SERVER_PROTOCOL')}\""
    match str(status_code := response.status_code)[0]:
        case '5':
            logging.error(f'{res} {status_code}')
        case '4':
            logging.warning(f'{res} {status_code}')
        case _:
            logging.info(f'{res} {status_code}')
    return response

@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def main():
    return render_template('index.html')

@app.route('/sell', methods=['GET'])
@app.route('/html/sell.html', methods=['GET'])
def sell():
    return render_template(
        'html/sell.html',
        list = [1, 2, 3, 3, 2, 1, 2, 1, 3],
        item = [
            ['CPU', 'I9 10900 X.'],
            ['RAM', '112 GB.'],
            ['SSD', '2 TB.'],
            ['HDD', '14 TB.']
        ]
    )

@app.route('/short', methods=['GET','POST'])
@app.route('/html/short.html', methods=['GET','POST'])
@limiter.limit("10 per 1 minute", methods=['POST'])
def short():
    if request.method == 'GET':
        return render_template(
            'html/short.html'
        )
    else:
        auth_data = {
            'secret': '6LdSC14hAAAAAJD8CX7IWrnwETwTMK_Eks46JcKf',
            'response': request.form['g-recaptcha-response']
        }
        auth_result = requests.post('https://www.google.com/recaptcha/api/siteverify', data=auth_data)
        if not auth_result.json()['success']:
            return render_template(
                'html/short.html',
                error_code = '驗證失敗'
            )
        else:
            url = request.form['URL']
            response = requests.get(f"https://transparencyreport.google.com/transparencyreport/api/v3/safebrowsing/status?site={url}")
            safe = response.text[17]
            match safe:
                case '2':
                    return render_template(
                        'html/short.html',
                        error_code = '惡意的網址'
                    )
                case _:
                    url = url[:-1] if url.endswith('/') else url
                    if (id := search_id(url)):
                        return render_template(
                            'html/short.html',
                            link = id
                        )
                    else: 
                        return render_template(
                            'html/short.html',
                            link = write_database(url)
                        )

@app.route('/url', methods=['GET'])
def no_url():
    return redirect(url_for('short'))

@app.route('/url/<id>', methods=['GET'])
def url(id: str):
    environ = request.environ
    if not environ.get('HTTP_UPGRADE_INSECURE_REQUESTS'):
        return redirect(url_for('short'))
    else:
        if (url := search_url(id)):
            return redirect(url)
        else:
            return render_template(
                'html/short.html',
                error_code = '未查詢到該網址'
            )

@app.route('/terms')
def terms():
    return render_template('html/Terms.html')

@app.route('/lib/lib.py')
@app.route('/test.py')
@app.route('/Run.py')
@app.route('/Database.db')
@app.route('/log.log')
def forbidden():
    abort(403)

if __name__ == "__main__":
    import sys

    from gevent import pywsgi
    app.config['DEBUG'] = True
    WebServer = pywsgi.WSGIServer(('0.0.0.0', 80), app)
    read_database()
    try:
        PrintLogMsg('Server STARTED')
        WebServer.serve_forever()
    except KeyboardInterrupt:
        database.commit()
        PrintLogMsg("Successfully saved the database")
        database.close()
        PrintLogMsg("Successfully disconnected from the database")
        PrintLogMsg('Server CLOSED')
        input('Press ENTER to continue...')
        sys.exit()
