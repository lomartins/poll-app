from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'secret string'


@app.route('/')
def home_page():
    return render_template('home-page.html', active_page='home', title='Poll App')


@app.route('/login')
def login_page():
    return render_template('login-page.html', active_page='login', title='Poll App')


@app.route('/create-poll')
def create_page():
    return render_template('create-page.html', active_page='create', title='Poll App')


def main():
    app.run(port=8080, debug=True)


if __name__ == '__main__':
    main()
