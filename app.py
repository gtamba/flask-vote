import os
import random
import json
import socket
import argparse
from passlib.hash import sha256_crypt

from datetime import datetime
from flask import Flask, request, make_response, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from models import User, Candidate, db, login_manager, load_user


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
  return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    # Redirect to voting page if authenticated
    if current_user.is_authenticated:
        return redirect(url_for('vote'))
    # Collect error message from failed login    
    if request.args.get('error') is not None:
      error = request.args.get('error')
    else:
      error = None

    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user is None or not user.check_password(request.form['password']):
            error = ('Invalid username or password')
            return redirect(url_for('login', error=error))
    
        login_user(user, remember=request.form.get('remember_me'))
        return redirect(url_for('vote'))
 
    return render_template('login.html', error=error)

@app.route('/vote', methods=['POST','GET'])
def vote():
    # Redirect to login if not authenticated
    if not current_user.is_authenticated:
      return redirect(url_for('login'))
    # Redirect to results route if voted
    if current_user.has_voted:
      return redirect(url_for('results'))
    # Skip Admin user for votes
    if current_user.is_privileged:
      return redirect(url_for('results'))
    # Else, add the user's vote to the tallies
    if request.method == 'POST':
        vote = request.form['vote']
        voted_candidate = Candidate.query.filter_by(id=vote).first() 
        voted_candidate.votes += 1
        current_user.has_voted = True
        db.session.commit()
        return redirect(url_for('results'))
 
    candidates = Candidate.query.all()        
    return render_template('vote.html', candidates=candidates)
  
@app.route('/results')
def results():
    # Show results if admin, else move to acknowledgement page
    if not current_user.is_privileged:
      return render_template('acknowledge.html', user=current_user)

    candidates = Candidate.query.all()        
    return render_template('results.html', candidates=candidates)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--db_dir', type=str, default='db-dump')
    parser.add_argument('--host', type=str, default='0.0.0.0')    
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--debug', type=int, default=1)

    args = parser.parse_args()

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, f'{args.db_dir}/app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.secret_key = 'NONPRODUCTIONAPPKEY_TEST123'

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():  
        db.create_all()
        db.session.commit()
        hostname = socket.gethostname()
           
        print("Checking for existing User records")
        any_users = User.query.first()
      
        if any_users:
            print(f"Loading from db dump at {app.config['SQLALCHEMY_DATABASE_URI']}")
            db.session.commit()
     
        else:
            print("Loading mock data records from mock-data")
            try:
                with open(os.path.join(basedir, 'mock-data/candidates.json')) as file:
                    candidate_data = json.load(file).get('candidates')
                    for candidate in candidate_data:
                        new_candidate = Candidate(name=candidate)
                        db.session.add(new_candidate)

                with open(os.path.join(basedir, 'mock-data/users.json')) as file:
                    user_data = json.load(file).get('users')
                    for user in user_data:
                        new_user = User(**user)
                        db.session.add(new_user)
                db.session.commit()
            except Exception as e:
              print(f"Loading from mock records failed {e}")

    
    app.run(host=args.host, port=args.port, debug=bool(args.debug))
