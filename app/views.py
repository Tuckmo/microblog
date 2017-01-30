from flask import render_template, flash, redirect, url_for, current_app, redirect, request, g, session
from flask.ext.login import login_user, logout_user, current_user, login_required
from .oauth import OAuthSignIn
from app import app, db, lm
from .forms import LoginForm
from .models import User



@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool'
        }
    ]
    return render_template('index.html', title="Home", user=user, posts=posts)

@app.before_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html',
                           title='Sign In')

@app.route('/authorize/<provider>')
def oauth_authorise(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    id,nickname, email = oauth.callback()
    if id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(id=id).first()
    if not user:
        user = User(nickname=nickname,email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user,True)
    return redirect(url_for('index'))