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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
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
    short_drinks = [drink.short() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": short_drinks
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
def get_drinks_details():
    drinks = Drink.query.all()
    short_drinks = [drink.long() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": short_drinks
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
def create_drinks():
    data = request.get_json()
    #validate data
    if data is None:
        abort(400, 'title and recipe must be present in JSON form.')
    if 'title' not in data or 'recipe' not in data:
        abort(400, 'title and recipe must be present in JSON form.')
    if not isinstance(data['title'], str):
        abort(400, 'title must be a string.')
    if data['title'] == '':
        abort(400, 'title can\'t be empty.')
    if not isinstance(data['recipe'], list): 
        abort(400, 'recipe must be an array.')
    if len(data['recipe']) == 0:
        abort(400, 'recipe can\'t be empty.')
    
    #create drink
    drink = Drink(
        title  = data['title'],
        recipe = json.dumps(data['recipe'])
    )
    try:
        drink.insert()
    except:
        abort(400, 'bad request')

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
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
def update_drinks(drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404, f'drink with id {drink_id} not found')
    
    data = request.get_json()
    #validate data
    if data is not None and 'title' in data:
        if not isinstance(data['title'], str):
            abort(400, 'title must be a string.')
        drink.title = data['title']

    if data is not None and 'recipe' in data:
        if not isinstance(data['recipe'], list): 
            abort(400, 'recipe must be an array.')
        drink.recipe = [json.dumps(data['recipe'])]

    try:
        drink.update()
    except:
        abort(400, 'bad request.')

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
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
def delete_drinks(drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404, f'drink with id {drink_id} not found')
    
    return jsonify({
        "success": True,
        "delete": drink_id
    })
    


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": error.description
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": error.description
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def notFound(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": error.description
                    }), 404


@app.errorhandler(400)
def notFound(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": error.description
                    }), 400



'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def authError(error):
    return jsonify({
                    "success": False, 
                    "error": error.status_code,
                    "message": error.error['description']
                    }), error.status_code


