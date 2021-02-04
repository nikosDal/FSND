from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from models import setup_db, Question, Category
import random

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r'/*': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        # set-up CORS headers
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # ----------------------------------------------------
    # ROUTES
    # ----------------------------------------------------
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            cats = Category.query.all()
        except Exception as e:
            app.log_exception(e)
            abort(500, description=f'Failed to query Categories: {e}')

        if cats is None:
            abort(404, description='No categories found')

        cat_dict = {cat.id: cat.type for cat in cats}
        return jsonify({
            'success': True,
            'categories': cat_dict
        })

    @app.route('/questions', methods=['GET'])
    def get_questions():

        # Handle pagination by getting page argument from request - default to page 1
        page_no = request.args.get('page', 1, int)
        start = (page_no - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        # Get all questions ordered by id
        try:
            questions = Question.query.order_by(Question.id).all()
        except Exception as e:
            app.log_exception(e)
            abort(500, description=f'Failed to query Questions: {e}')

        if not questions:
            abort(404, description='No questions found')

        # Build page for questions
        page_questions = [question.format() for question in questions[start:end]]

        # Get categories as they are also needed for the response
        categories = Category.query.all()
        cat_dict = {cat.id: cat.type for cat in categories}

        return jsonify({
            'success': True,
            'questions': page_questions,
            'total_questions': len(questions),
            'current_category': 1,   # WHAT IS THIS MEANT TO SHOW??
            'categories': cat_dict
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question_by_id(question_id):
        try:
            question = Question.query.get(question_id)
        except Exception as e:
            app.log_exception(e)
            abort(500, description=f'Failed to query questions: {e}')

        if not question:
            abort(404, description=f'No question found with id {question_id}')

        try:
            question.delete()
            return jsonify(success=True)
        except Exception as e:
            app.log_exception(e)
            abort(500, description=f'Failed to delete question: {e}')

    @app.route('/questions', methods=['POST'])
    def add_question():
        try:
            question = Question(
                question=request.json['question'],
                answer=request.json['answer'],
                category=request.json['category'],
                difficulty=request.json['difficulty']
            )
        except KeyError as e:
            # Missing one of required parameters from request JSON
            abort(422, description=f'Missing question parameter: {e}')
        except ValueError as e:
            # Bad parameter given in JSON
            abort(400, description=f'Bad parameter given: {e}')

        try:
            question.insert()
            return jsonify(success=True)
        except Exception as e:
            app.log_exception(e)
            abort(500)

    @app.route('/questions/search', methods=['POST'])
    def get_questions_by_search():
        if 'searchTerm' not in request.json.keys():
            abort(422, description='Missing searchTerm')

        search_term = request.json['searchTerm']
        try:
            questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        except Exception as e:
            app.log_exception(e)
            abort(500, description=f'Failed to query Questions: {e}')

        if not questions:
            abort(404, description=f'No questions found for searchTerm {search_term}')

        formatted_questions = [question.format() for question in questions]
        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'current_category': 1   # AGAIN, WHAT IS THIS MEANT TO BE AND HOW IS IT USED??
        })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_for_category(category_id):
        try:
            questions = Question.query.filter_by(category=category_id).all()
        except Exception as e:
            app.log_exception(e)
            abort(500, description=f'Failed to query Questions: {e}')

        if not questions:
            abort(404, description=f'No questions found under Category {category_id}')

        formatted_questions = [question.format() for question in questions]
        try:
            category = Category.query.filter_by(id=category_id).one_or_none()
        except Exception as e:
            app.log_exception(e)
            abort(500, description=f'Failed to query Category: {e}')

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'current_category': category.format()
        })

    @app.route('/quizzes', methods=['POST'])
    def get_next_question():
        try:
            category = request.json['quiz_category']
            prev_questions = request.json['previous_questions']
        except KeyError as e:
            abort(422, description=f'Missing required parameter: {e}')

        try:
            # Get questions for the given category (if not 0), filtering out previous question ids
            subquery = Question.query.filter(~Question.id.in_(prev_questions))
            if category['id'] == 0:
                available_questions = subquery.all()
            else:
                available_questions = subquery.filter(Question.category == category['id']).all()
        except Exception as e:
            app.log_exception(e)
            abort(500, description=f'Failed to query Question: {e}')

        # Return random question if any available, else return null
        questions_left = len(available_questions)
        next_question = None
        if questions_left > 0:
            next_question = available_questions[random.randint(0, questions_left-1)].format()

        return jsonify({
            'success': True,
            'question': next_question
        })

    # ----------------------------------------------------
    # ERROR HANDLERS
    # ----------------------------------------------------
    @app.errorhandler(404)
    def not_found_error(err):
        return jsonify({
            'success': False,
            'error': 404,
            'message': str(err)
        }), 404

    @app.errorhandler(422)
    def unprocessable_error(err):
        return jsonify({
            'success': False,
            'error': 422,
            'message': str(err)
        }), 422

    @app.errorhandler(500)
    def internal_error(err):
        return jsonify({
            'success': False,
            'error': 500,
            'message': str(err)
        }), 500

    return app
