from flask import Flask, jsonify

def create_app(test_config=None):
    app = Flask(__name__)

    @app.route('/')
    def hello():
        return jsonify({'message': 'HELLO MOPS'})

    @app.route('/smiley')
    def helloSmiley():
        return ':-)'

    return app