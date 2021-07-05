from typing import List

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, func
from flask_assets import Environment, Bundle
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, instance_relative_config=False)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:15432/poll_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret string'

assets = Environment(app)
style_bundle = Bundle(
    'vendor/less/*.less',
    filters='less,cssmin',
    output='dist/css/style.min.css',
    extra={'rel': 'stylesheet/css'}
)
create_poll_js = Bundle(
    'src/js/create-poll.js',
    filters='jsmin',
    output='dist/js/create-poll.min.js'
)
script_bundle_js = Bundle(
    'src/js/script.js',
    filters='jsmin',
    output='dist/js/script.min.js'
)
assets.register('main_styles', style_bundle)
assets.register('main_js', script_bundle_js)
assets.register('create_poll_js', create_poll_js)
style_bundle.build()
script_bundle_js.build()
create_poll_js.build()

db = SQLAlchemy(app)


class Poll(db.Model):
    poll_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    author = db.Column(db.String(32))
    published = db.Column(db.String(32))

    def __init__(self, name, author, published):
        self.name = name
        self.author = author
        self.published = published

    def __repr__(self):
        return '<poll_id {}>'.format(self.poll_id)

    def serialize(self):
        return {
            'poll_id': self.poll_id,
            'name': self.name,
            'author': self.author,
            'published': self.published
        }


class PollOption(db.Model):
    option_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poll_id = db.Column(db.Integer, ForeignKey('poll.poll_id'))
    value = db.Column(db.String(64))

    def __init__(self, poll_id, value):
        self.poll_id = poll_id
        self.value = value


class Vote(db.Model):
    vote_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poll_id = db.Column(db.Integer, ForeignKey('poll.poll_id'))
    option_id = db.Column(db.Integer, ForeignKey('poll_option.option_id'))
    user = db.Column(db.String(32))

    def __init__(self, poll_id, option_id, user):
        self.poll_id = poll_id
        self.option_id = option_id
        self.user = user


class QuestionResult:
    def __init__(self, value: str, count: int, percent: float):
        self.value = value
        self.count = count
        self.percent = percent


class PollResultPage:
    def __init__(self, poll: Poll, questions_result: List[QuestionResult]):
        self.poll = poll
        self.questions_result = questions_result


@app.route('/poll/<poll_id>/')
def poll_page(poll_id):
    try:
        poll_id = int(poll_id)
    except ValueError:
        return 'Id invalido'

    current_poll = db.session.query(Poll).filter_by(poll_id=poll_id).first()
    if current_poll is None:
        return 'Id invalido'

    options = db.session.query(PollOption).filter_by(poll_id=poll_id).all()
    return render_template('poll.html',
                           title=current_poll.name,
                           action=url_for('vote', poll_id=poll_id),
                           poll_title=current_poll.name,
                           poll_options=options)


@app.route('/poll/<poll_id>/vote/', methods=['POST'])
def vote(poll_id):
    user = 'João'
    value = request.form['poll_option']
    option = db.session.query(PollOption).filter_by(poll_id=poll_id, value=value).first()
    entry = Vote(poll_id=poll_id, option_id=option.option_id, user=user)
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for('poll_page', poll_id=poll_id))


@app.route('/poll/<poll_id>/results')
def poll_result(poll_id):
    current_poll: Poll = db.session.query(Poll).filter_by(poll_id=poll_id).first()
    questions = db.session.query(PollOption.value, func.count(Vote.option_id)).join(Vote, isouter=True).where(
        PollOption.poll_id == poll_id).group_by(PollOption.option_id).all()
    questions_result = []
    total = 0
    for question in questions:
        total += question[1]

    for question in questions:
        value = str(question[0])
        count = int(question[1])
        if total > 0:
            percent = (count / total) * 100
        else:
            percent = 0
        questions_result.append(QuestionResult(value=value, count=count, percent=percent))
    data = PollResultPage(current_poll, questions_result=questions_result)
    return render_template('poll-result.html', data=data)


@app.route('/create/')
def create_poll():
    return render_template('create-poll.html')


@app.route('/save-poll', methods=['POST'])
def save_poll():
    title = request.form.get('title')
    options = request.form.getlist('options')

    poll = Poll(name=title, author='Joao', published='04/07/2021')
    db.session.add(poll)
    db.session.commit()

    for option in options:
        if option != '':
            db.session.add(PollOption(poll_id=poll.poll_id, value=option))
    db.session.commit()

    return redirect(url_for('manage_poll', poll_id=poll.poll_id))


@app.route('/poll/<poll_id>/manage/')
def manage_poll(poll_id):
    try:
        poll_id = int(poll_id)
    except ValueError:
        return 'Id invalido'

    current_poll = db.session.query(Poll).filter_by(poll_id=poll_id).first()
    if current_poll is None:
        return 'Id invalido'

    return render_template('poll-manage.html', poll_id=poll_id, poll_title=current_poll.name)


def main():
    db.create_all()
    app.run(port=8080, debug=True)


if __name__ == '__main__':
    main()
