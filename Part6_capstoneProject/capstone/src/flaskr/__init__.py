from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json

from models import setup_db, Player, Team, db

app = Flask(__name__)
setup_db(app)
migrate = Migrate(app, db)

@app.route('/players', methods=['GET'])
def get_players():
    players = Player.query.all()

    outplayers = [player.format() for player in players]

    return jsonify({
        'success': True,
        'players': outplayers
    })

@app.route('/teams', methods=['GET'])
def get_teams():
    teams = Team.query.all()

    outteams = [team.format() for team in teams]

    return jsonify({
        'success':True,
        'teams':outteams
    })

@app.route('/players', methods=['POST'])
def create_player():
    try:
        body = request.get_json()

        new_name = body.get('name', None)
        new_skill = body.get('skill', None)

        player = Player(name=new_name, skill=new_skill)
        player.insert()

        return jsonify({
            'success':True,
            'player':player.format()
        })
    except:
        abort(422)

@app.route('/teams/<int:team_id>', methods=['PATCH'])
def update_team(team_id):
    try:
        old_team = Team.query.filter(Team.id == team_id).one_or_none()

        new_team = request.get_json()

        new_name = new_team.get('name', None)
        new_city = new_team.get('city', None)

        if new_name is not None:
            old_team.name = new_name
        if new_city is not None:
            old_team.city = new_city

        old_team.update()

        return jsonify({
            'success': True,
            'team': old_team.format()
        })
    
    except:
        abort(422)

@app.route('/players/<int:player_id>', methods=['DELETE'])
def delete_player(player_id):
    try:
        player = Player.query.filter(Player.id == player_id).one_or_none()

        if player is None:
            abort(404)
        
        player.delete()

        return jsonify({
            'success': True,
            'delete_id': player_id
        })
    except:
        abort(422)


        

        
