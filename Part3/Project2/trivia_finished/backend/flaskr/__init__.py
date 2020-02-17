import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
    return response


  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    categories_json = [cat.format() for cat in categories]

    if len(categories_json) == 0:
      abort(404)

    categories_api_format = {}
    for cat in categories_json:
      categories_api_format[str(cat['id'])] = cat['type']

    print(categories_api_format)

    return jsonify({
      'success': True,
      'categories': categories_api_format,
      'total_categories': len(categories_json)
    })

  @app.route('/questions', methods=['GET'])
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    
    current_questions = paginate_questions(request, selection)

    categories = Category.query.order_by(Category.id).all()
    categories_json = [cat.format() for cat in categories]

    if len(current_questions) == 0:
      abort(404)


    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories': categories_json  
    })


  '''
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  ''' 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success': True
      })
    except:
      abort(422)


  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    search = body.get('searchTerm', None)

    try:

      if search:
        selection = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()
        
        current_questions = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.id).all()
        categories_json = [cat.format() for cat in categories]

        if len(current_questions) == 0:
          abort(404)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(Question.query.all()),
          'categories': categories_json  
        })

      else:

        question = Question(
                      question=new_question,
                      answer=new_answer,
                      category=new_category,
                      difficulty=new_difficulty )
        question.insert()

        return jsonify({
          'success': True
        })
    except:
      abort(422)


  '''
  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
  def get_questions_by_cat(cat_id):
    selection = Question.query.filter(Question.category == cat_id).all()
    
    current_questions = paginate_questions(request, selection)

    categories = Category.query.filter(Category.id == cat_id).all()
    categories_json = [cat.format() for cat in categories]

    if len(current_questions) == 0:
      abort(404)

    categories_api_format = {}
    for cat in categories_json:
      categories_api_format[str(cat['id'])] = cat['type']

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'current_category': categories_api_format,
      'categories': categories_api_format 
    })

  '''

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quizz():
    body = request.get_json()

    #print(body)

    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)

    questions = Question.query.filter(Question.category == quiz_category['id']).all()
    formatted_questions = [question.format() for question in questions]

    #print(formatted_questions)

    #choose the first question which is not in the previous questions
    for question in formatted_questions:
      if question['id'] not in previous_questions:
        out_question = question
        break
    
    print(out_question)

    return jsonify({
      'success': True,
      'question': out_question
    })


  '''

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "Not found"
    })

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessible"
    })
  
  return app

    