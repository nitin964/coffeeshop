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
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
@TODO done
implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks")
#@requires_auth('get:drinks')
def retrieve_drinks():
    selection = Drink.query.order_by(Drink.id).all()
    print ("working")
    return jsonify(
        {
            'success': True,
            'drinks': [drink.short() for drink in selection]
        }
    )

'''
@TODO done
implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(jwt):
    selection = Drink.query.order_by(Drink.id).all()

    return jsonify(
        {
            'success': True,
            'drinks': [drink.long() for drink in selection]
        }
    )

'''
@TODO done
implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def add_drink(jwt):
    body = request.get_json()
    new_title = body.get("title", None)
    new_recipe = json.dumps(body['recipe'])

    if new_title in (None, ''):
        abort(422)
    if new_recipe in (None, ''):
        abort(422)

    cat = Drink.query.filter(Drink.title == new_title).one_or_none()

    if cat is not None:
        abort(422)

    try:
        drink = Drink(title=new_title, recipe=new_recipe)
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.id
        })
    except:
        abort(422)

'''
@TODO done
implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def modify_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    
    if drink is None:
        abort(404)
    
    try:
        body = request.get_json()
        if 'title' in body:
            drink.title = body.get("title")
        
        if 'recipe' in body:
            drink.recipe = json.dumps(body['recipe'])
        
        drink.update()
        
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        abort(422)

'''
@TODO done
implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    
    if drink is None:
        abort(404)
    
    try:
        drink.delete()

        return jsonify({
            'success': True,
            'drinks': drink_id
        })
    except:
        abort(422)

# Error Handling
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
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(405)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405

@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401
'''
@TODO done
implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO done
implement error handler for AuthError
    error handler should conform to general task above
'''
