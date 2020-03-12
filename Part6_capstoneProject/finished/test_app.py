import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Player, Team

class SportAppTestCase(unittest.TestCase):

    def setUp(self):
        #Define test variables and initialize app
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "capstone_test"
        self.database_path = "postgres://{}/{}".format('postgres:1234@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    """get players endpoint"""
    def test_get_players(self):
        res = self.client().get('/players')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['players'])
        
    def test_get_players_not_allowed(self):
        res = self.client().get('/players/1', json={})
        data = json.loads(res.data)

        self.assertEqual(data['error'], 405)
        self.assertEqual(data['success'], False)

    """get teams endpoint"""
    
    def test_get_teamss(self):
        res = self.client().get('/teams')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['teams'])
        
    def test_get_teamss_not_allowed(self):
        res = self.client().get('/teams/1', json={})
        data = json.loads(res.data)

        self.assertEqual(data['error'], 405)
        self.assertEqual(data['success'], False)
    
    """post player endpoint"""

    def test_create_player(self):
        res = self.client().post('/players', 
                json = {
                    'name': "HanniBanani8",
                    'skill': 11
                })
        
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_create_player_not_allowed(self):
        res = self.client().post('/players/44', json={})
        data = json.loads(res.data)

        self.assertEqual(data['error'], 405)
        self.assertEqual(data['success'], False)

    """patch team endpoint"""
    def test_patch_team(self):
        res = self.client().patch('/teams/1', json={'city':"London"})
        data = json.loads(res.data)

        team = Team.query.filter(Team.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(team.format()['city'], "London")

    def test_patch_team_unprocessable(self):
        res = self.client().patch('/teams/1')
        data = json.loads(res.data)

        self.assertEqual(data['error'], 422)
        self.assertEqual(data['success'], False)

    """delete player endpoint"""
    def test_delete_player(self):
        res = self.client().delete('/players/1')
        data = json.loads(res.data)

        player = Player.query.filter(Player.id == 1).one_or_none()

        self.assertEqual(data['success'], True)
        self.assertEqual(player, None)
    
    def test_player_does_not_exist(self):
        res = self.client().delete('/players/11111')
        data = json.loads(res.data)

        self.assertEqual(data['error'], 422)
        self.assertEqual(data['success'], False)
        

if __name__ == "__main__":
    unittest.main()
