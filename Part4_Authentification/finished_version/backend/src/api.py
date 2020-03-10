import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

#db_drop_and_create_all()

@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    outDrinks = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': outDrinks
    })

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    outDrinks = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': outDrinks
    })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):

    try:
        #get the drink from the request
        body = request.get_json()

        new_title = body.get('title', None)
        print(new_title)
        new_recipe = body.get('recipe', None)

        #solve the double quote problem
        recipeString = "[{"
        try:
            recipeString = recipeString + "\"color\":" + "\"" + new_recipe["color"] + "\"," 
            recipeString = recipeString + "\"name\":" + "\"" + new_recipe["name"] + "\","
            partsString = str(new_recipe["parts"])
            recipeString = recipeString + "\"parts\":" + partsString
            recipeString = recipeString + "}]"
        except Exception as e:
            print(e)
  
        try:
            drink = Drink(title=new_title, recipe=recipeString)
            drink.insert()
        except Exception as e:
            print(e)

        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.short()
        })
    except:
        abort(422)

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, drink_id):
    try:
        new_drink = request.get_json()

        #get the drink from the request
        old_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        try:
            if new_drink.get('title', None) is not None:
                old_drink.title = new_drink.get('title', None)
            if new_drink.get('recipe', None) is not None:
                old_drink.recipe = new_drink.get('recipe', None)

            old_drink.update()
            print(old_drink)
        except Exception as e:
            print(e)

        try:
            out = []
            out.append(old_drink.short())

            return jsonify({
                'success': True,
                'drinks': out
            })
        except Exception as e:
            print(e)

    except:
        abort(422)

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except:
        abort(422)

'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def nofound(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "no found"
                    }), 422


@app.route('/authTest')
@requires_auth('get:drinks-detail')
def test_auth(payload):
    print('executing test auth')
    print(payload)
    return 'Testin auth system'
