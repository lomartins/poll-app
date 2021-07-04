from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:15432/poll_database'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

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


class Vote(db.Model):
    vote_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poll_id = db.Column(db.Integer, ForeignKey("poll.poll_id"))
    user = db.Column(db.String(32))
    value = db.Column(db.String(64))

    def __init__(self, poll_id, user, value):
        self.poll_id = poll_id
        self.user = user
        self.value = value


class PollOption(db.Model):
    option_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poll_id = db.Column(db.Integer, ForeignKey("poll.poll_id"), primary_key=True)
    value = db.Column(db.String(64))

    def __init__(self, poll_id, value):
        self.poll_id = poll_id
        self.value = value


@app.route("/poll/<poll_id>")
def poll(poll_id):
    try:
        poll_id = int(poll_id)
    except ValueError:
        return "Id invalido"

    current_poll = db.session.query(Poll).filter_by(poll_id=poll_id).first()
    if current_poll is None:
        return "Id invalido"

    options = db.session.query(PollOption).filter_by(poll_id=poll_id).all()
    return render_template('poll.html',
                           title=current_poll.name,
                           action=url_for('vote', poll_id=poll_id),
                           poll_title=current_poll.name,
                           poll_options=options)


@app.route("/poll/<poll_id>/vote/", methods=['POST'])
def vote(poll_id):
    user = "João"
    value = request.form["poll_option"]
    entry = Vote(poll_id=poll_id, user=user, value=value)
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for('poll', poll_id=poll_id))


def main():
    db.create_all()
    app.run(port=8080, debug=True)


if __name__ == '__main__':
    main()
