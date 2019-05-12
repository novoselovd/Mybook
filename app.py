from flask import Flask, render_template, request, make_response, jsonify, redirect, flash
from flask_bootstrap import Bootstrap
import requests
import json

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
Bootstrap(app)

headers = {'Accept': 'application/json; version=5'}
loginUrl = 'https://mybook.ru/api/auth/'
booksUrl = 'https://mybook.ru/api/bookuserlist/'


@app.route('/', methods=['GET', 'POST'])
def index():
    # Checking if user is authorized
    if request.cookies.get('session'):
        try:
            # Getting cookies
            c = {'session': request.cookies.get('session')}

            # Requesting user's books list
            r = requests.get(booksUrl,  headers=headers, cookies=c)
            next = r.json()['meta']['next']

            books = r.json()['objects']  # List of all user's books

            # Adding books from all the pages to books list
            while next:
                r = requests.get('https://mybook.ru' + next, headers=headers, cookies=c)
                books.extend(r.json()['objects'])

                next = r.json()['meta']['next']

            # If no books added to 'My books'
            if not books:
                books = 'Empty'

            return render_template('index.html', data=books)
        except Exception as e:
            print(e)
    else:
        # Trying to authorize
        if request.method == 'POST':
            email = request.form.get('email')
            pwd = request.form.get('pwd')

            try:
                auth = requests.post(loginUrl, json={"email": email, "password": pwd})
                cookies = requests.utils.dict_from_cookiejar(auth.cookies)
                response = make_response(redirect('/'))
                response.set_cookie('session', cookies['session'])

                return response
            except Exception as e:
                try:
                    flash(list(dict(auth.json()).values())[0][0])
                except Exception as e:
                    pass

    return render_template('index.html', data=None)


@app.route('/signout', methods=['GET', 'POST'])
def signout():
    # Removing cookies
    res = make_response(redirect('/'))
    res.set_cookie('session', 'None', max_age=0)

    return res


if __name__ == '__main__':
    app.run()
