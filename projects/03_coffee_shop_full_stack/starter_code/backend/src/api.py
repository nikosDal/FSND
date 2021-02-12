from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()


@app.route('/')
def index():
    return 'hello'


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    if 'title' not in request.json:
        abort(400, description='missing title from drink details')
    if 'recipe' not in request.json:
        abort(400, description='missing recipe from drink details')
    new_drink = Drink(title=request.json['title'], recipe=request.json['recipe'])

    app.logger.info(f'New Drink being added: {new_drink.long()}')
    try:
        new_drink.insert()
    except Exception as e:
        app.log_exception(e)
        abort(500, description=f'failed to save new drink titled {request.json["title"]} due to {e}')

    return jsonify({
        'success': True,
        'drinks': [new_drink.long()]
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)
    if 'title' in request.json:
        drink.title = request.json['title']
    if 'recipe' in request.json:
        drink.recipe = json.dumps(request.json['recipe'])

    app.logger.info(f'Drink {drink_id} being updated: {drink.long()}')
    try:
        drink.update()
    except Exception as e:
        app.log_exception(e)
        abort(500, description=f'Failed to update drink with id {drink_id} due to {e}')

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)

    app.logger.info(f'Drink {drink_id} being deleted')
    try:
        drink.delete()
    except Exception as e:
        abort(500, description=f'Failed to delete drink with id {drink_id} due to {e}')

    return jsonify({
        'success': True,
        'delete': drink_id
    })


# -----------------------------------------------
# ERROR HANDLING
# -----------------------------------------------
@app.errorhandler(400)
def bad_request(e):
    return jsonify({
        'success': False,
        'error': 400,
        'message': f'bad request - {str(e)}'
    }), 400


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'success': False,
        'error': 500,
        'message': f'internal error - {str(e)}'
    }), 500


@app.errorhandler(422)
def unprocessable(e):
    return jsonify({
        "success": False,
        "error": 422,
        "message": f"unprocessable - {str(e)}"
        }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404


@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify({
        'success': False,
        'error': e.status_code,
        'message': e.error
    }), e.status_code
