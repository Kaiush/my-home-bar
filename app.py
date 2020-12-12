from typing import Any, List

import bcrypt
from flask import Flask, abort, render_template, request, session, url_for
from playhouse.shortcuts import model_to_dict
import peewee
from werkzeug.utils import redirect

from Models import (
    Users, Alcohols, Cocktails, Shelfs, Recipes, database
)


app = Flask(__name__)
app.secret_key = "secret key"


@app.before_request
def _db_connect():
    database.connect()


@app.teardown_request
def _db_close(_):
    if not database.is_closed():
        database.close()


@app.route('/delete/<drink>')
def delete(drink):
    if session.get('user_id') is None:
        return abort(403, 'You are not allowed to change shelfs!')
    alc_id = Alcohols.select(Alcohols.id).where(Alcohols.name == drink).get()
    q = Shelfs.delete().where((Shelfs.alc_id == alc_id) & (Shelfs.user_id == session.get('user_id'))).execute()
    return redirect(url_for('shelf'))

@app.route('/shelf', methods=['GET', 'POST'])
def shelf():
    if session.get('user_id') is None:
        return redirect(url_for('home'))
    if request.method == 'GET':
        drinks = {}
        alcohols = {}
        q = Shelfs.select(Shelfs,Alcohols).join(Alcohols).where(session.get('user_id') == Shelfs.user_id)
        for line in q.objects():
            drinks[line.name] = line.bottles
        for line in Alcohols.select():
            alcohols[line.id] = line.name

        return render_template('shelf.html', my_shelf=drinks, alcohols=alcohols, username=session.get('username'))

    drink_type = request.form['drink']
    drinks_volume = request.form['amount']
    new_drink = Shelfs.replace(user_id=session.get('user_id'), alc_id=drink_type, bottles=drinks_volume)
    new_drink.execute()
    return redirect(url_for('shelf'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if session.get('username') is None:
            return render_template('register.html', username=session.get('username'))
        else:
            return redirect(url_for('shelf'))
    
    salt = bcrypt.gensalt(prefix=b'2b', rounds=10)
    unhashed_password = request.form['password'].encode('utf-8')
    hashed_password = bcrypt.hashpw(unhashed_password, salt)
    fields = {
        **request.form,
        'password': hashed_password,
        'level': 1,
    }
    user = Users(**fields)
    try:
        user.save()
    except peewee.IntegrityError:
        return 'User already exists!'
    return 'Success!'

@app.route('/availables')
def availables():
    if session.get('username') is None:
        return redirect(url_for('home'))
    q = Cocktails.select(Cocktails.name, Cocktails.abv, Cocktails.description).where(
            Cocktails.id.not_in(
                Recipes.select(Recipes.cocktail_id).where(
                        Recipes.alc_id.not_in(
                            Shelfs.select(Shelfs.alc_id).where(
                                Shelfs.user_id == session.get('user_id')
                                )
                            )
                        )
                    )
            )
    return render_template('availables.html', available_cocktails=q.dicts(), username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('username') is None:
            return render_template('login.html')
        else:
            return redirect(url_for('shelf'))

    username = request.form['username']
    if username is None:
        return abort(400, 'No username supplied')

    try:
        user = Users.select().where(Users.username == username).get()
    except peewee.DoesNotExist:
        return abort(404, f'User {username} does not exists')
    
    password = request.form['password'].encode('utf-8')
    real_password = str(user.password).encode('utf-8')
    if not bcrypt.checkpw(password, real_password):
        return abort(403, 'Username and password does not match')

    session['user_id'] = user.id
    session['username'] = user.username
    session['name'] = user.name
    return redirect(url_for('home'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    for session_value in ('user_id', 'username', 'name', 'level'):
        session.pop(session_value, None)
    return redirect(url_for('home'))


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('shelf'))
    return render_template('index.html', username=session.get('username'))


if __name__ == '__main__':
    app.run(debug=True)
