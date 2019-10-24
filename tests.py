from flask_testing import TestCase
import os
from models import db, login_manager, User, Candidate
import unittest
import flask_testing
from flask import Flask
import json
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from app import app

basedir = os.path.abspath(os.path.dirname(__file__))

class ObjectTest(TestCase):
    render_templates = False

    def create_app(self):
        app.config['TESTING'] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'db-dump/test_app.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ECHO'] = False
        app.secret_key = "TESTSSECRETKEY"

        db.init_app(app)
        login_manager.init_app(app)
        app.app_context().push()

        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class ApplicationTest(ObjectTest):
    def test_mock_db(self):
        with open(os.path.join(basedir, 'mock-data/users.json')) as file:
            user_data = json.load(file).get('users')
            for user in user_data:
                new_user = User(**user)
                db.session.add(new_user)
        with open(os.path.join(basedir, 'mock-data/candidates.json')) as file:
            candidates = json.load(file).get('candidates')
            for candidate in candidates:
                new_candidate = Candidate(name=candidate)
                db.session.add(new_candidate)

        db.session.commit()
        all_users = User.query.all()
        all_candidates = Candidate.query.all()

        assert len(all_users) == 7
        assert len(all_candidates) == 4
        
        assert all_candidates[0].votes == 0
        assert all_candidates[1].votes == 0
        assert all_candidates[2].votes == 0
        assert all_candidates[3].votes == 0

    def test_login(self):
        user = User(email="test", password="testpass")
        db.session.add(user)
        db.session.commit()

        vote_response = self.client.post("/vote", data={"email": "test", "password": "testpass"}, follow_redirects=True)
        self.assert_template_used('login.html')


if __name__ == '__main__':
    unittest.main()
