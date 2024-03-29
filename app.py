from flask import Flask, jsonify,  make_response, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt, verify_jwt_in_request
from flask_httpauth import HTTPBasicAuth
import pandas as pd
from pathlib import Path
import numpy as np
import datetime
import io

# Set path to current directory
path = str(Path(__file__).parent.absolute()) + '/'

app = Flask(__name__) # create an app instance
app.config["DEBUG"] = True # enable debugging, auto-reload

# Convert csv to json
def csv_to_json(filename, header=None):
    data = pd.read_csv(filename, header=header)
    data.replace({np.nan: None}, inplace=True)
    return data.to_dict(orient='records') 

# Load data
data = csv_to_json(path + './static/horse.csv', header=0)


# Routes for API v1 (no authentication) #######################################################################

# Home page
@app.route('/', methods=['GET'])
def home():
    return "<h1>API is working</h1><p>Flask is running.</p>"

# A route to return all of the available entries in our catalog.
@app.route('/api/v1/resources/horses/all', methods=['GET'])
def api_all():
    return jsonify(data)

# A route to return a specific horse by id
@app.route('/api/v1/resources/horse', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."

    # Create an empty list for our results
    results = []

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    for horse in data:
        if horse['hospital_number'] == id:
            results.append(horse)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)

# API Documentation vor v1
@app.route('/api/v1/doc', methods=['GET'])
def api_doc():
    return '''
                        <h1>API Documentation</h1>
                        <p>API for horse data</p> 
                        <table>
                        <tr>
                        <th>Endpoint</th>
                        <th>Method</th>
                        <th>Parameters</th>
                        </tr>
                        <tr>
                            <td>
                                <a href='./resources/horses/all'>/api/v1/resources/horses/all</a>
                            </td>
                        <td>GET</td>
                        <td>None</td>
                        </tr>
                        <tr>
                        <td><a href='./resources/horse?id=530101'>/api/v1/resources/horse</a></td>
                        <td>GET</td>
                        <td>id</td>
                        </tr>
                        </table>
                        '''

# API v2 (authentication) ####################################################################################

# Set up authentication BasicAuth and JWT
users = {'nifi': 'nifi'}

auth = HTTPBasicAuth()

app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)
EXPRIATION_TOKEN_SECONDS = 3600
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=3600)


# Error handling for unauthorized access
@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

# Verify password for user
@auth.verify_password
def verify_password(username, password):
    if username in users and password == users.get(username):
        return True
    return False

# Routes for API v2

#Token retrieval
@app.route('/api/v2/login', methods=['GET'])
@auth.login_required
def login():
    username = auth.current_user()

    # Generate a new token for the user
    access_token = create_access_token(identity=username, fresh=True)
    return jsonify(access_token=access_token, expire_in=EXPRIATION_TOKEN_SECONDS), 200


@app.route('/api/v2/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# A route to return all of the available entries in our catalog. jwt_required() is used to protect the route
@app.route('/api/v2/resources/horses/all', methods=['GET'])
@jwt_required()
def api_all_v2():
    return jsonify(data)                        

# A route to return a specific horse by id. jwt_required() is used to protect the route
@app.route('/api/v2/resources/horse', methods=['GET'])
@jwt_required()
def api_id_v2():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return jsonify(Error="No id field provided. Please specify an id."), 400

    # Create an empty list for our results
    results = []

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    for horse in data:
        if horse['hospital_number'] == id:
            results.append(horse)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)

@app.route('/api/v2/resources/idtierce', methods=['GET'])
@jwt_required()
def api_idtierce_v2():
    # Return a random tierce of ids of horses
    np.random.seed(datetime.datetime.now().day)
    winners = np.random.choice([h['hospital_number'] for h in data], 3, replace=False)
    return jsonify(winners=winners.tolist())

@app.route('/api/v2/resources/validateHorses_JSON', methods=['POST'])
@jwt_required()
def api_validateHorses_JSON_content_v2():
    # Validate a json content with horse data
    # Check if the body request is json
    if not request.is_json:
        return jsonify(message='The request is not json'), 400
    try:
        reqContent = request.get_json()
        print(reqContent[0].keys())
        if set(reqContent[0].keys()) == set(data[0].keys()):
            return jsonify(message='The json content is valid'), 200
    except Exception as e:
        print('error in json', e)
        return jsonify(message='The request is not json'), 400
    return jsonify(message='The json content is not valid'), 400

@app.route('/api/v2/resources/validateHorse_JSON', methods=['POST'])
@jwt_required()
def api_validateSingleHorse_JSON_content_v2():
    # Validate a json content with a single horse data
    # Check if the body request is json
    if not request.is_json:
        return jsonify(message='The request is not json'), 400
    try:
        reqContent = request.get_json()
        print(reqContent.keys())
        if set(reqContent.keys()) == set(data[0].keys()):
            return jsonify(message='The json content is valid'), 200
    except Exception as e:
        return jsonify(message='The request is not json'), 400
    return jsonify(message='The json content is not valid'), 400

@app.route('/api/v2/resources/validateHorses_CSV', methods=['POST'])
#@jwt_required()
def api_validateHorses_CSV_content_v2():
    #validate a csv content with horse data
    # Check if the body request is csv
    requestContent = request.get_data()
    if not requestContent:
        return jsonify(message='The request is not csv'), 400
    try:
        reqContent = pd.read_csv(io.StringIO(requestContent.decode('utf-8')))
        if set(reqContent.columns) == set(data[0].keys()):
            return jsonify(message='The csv content is valid'), 200
    except Exception as e:
        return jsonify(message='The request is not csv'), 400
    return jsonify(message='The csv content is not valid'), 400


# API Documentation vor v2
@app.route('/api/v2/doc', methods=['GET'])
def api_doc_v2():
    return '''
                        <h1>API Documentation</h1>
                        <p>API for horse data</p> 
                        <table>
                        <tr>
                        <th>Endpoint</th>
                        <th>Method</th>
                        <th>Parameters</th>
                        <th>Authentication</th>
                        <th>Response</th>
                        </tr>

                        <tr>
                            <td>
                                <a href= './login'>/api/v2/login</a>
                            </td>
                            <td>GET</td>
                            <td>None</td>
                            <td>Basic Auth</td>
                            <td>Return an access_token</td>
                        </tr>

                        <tr>
                            <td>
                                <a href= './protected'>/api/v2/protected</a>
                            </td>
                            <td>GET</td>
                            <td>None</td>
                            <td>JWT</td>
                            <td>Return a login validation</td>
                        </tr>

                        <tr>
                            <td>
                                <a href='./resources/horses/all'>/api/v2/resources/horses/all</a>
                            </td>
                            <td>GET</td>
                            <td>None</td>
                            <td>JWT</td>
                            <td>Return all horses</td>
                        </tr>

                        <tr>
                            <td><a href='./resources/horse?id=530101'>/api/v2/resources/horse</a></td>
                            <td>GET</td>
                            <td>id</td>
                            <td>JWT</td>
                            <td>Return a specific horse by id</td>
                        </tr>
                        </table>
                        '''


# ERROR HANDLING ##############################################################################################

# Error handling for API
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.errorhandler(500)
def internal_server_error(e):
    return "<h1>500</h1><p>Internal Server Error</p>", 500

@app.errorhandler(405)
def method_not_allowed(e):
    return "<h1>405</h1><p>Method Not Allowed</p>", 405

@app.errorhandler(400)
def bad_request(e):
    return "<h1>400</h1><p>Bad Request</p>", 400

@app.errorhandler(403)
def forbidden(e):
    return "<h1>403</h1><p>Forbidden</p>", 403

@app.errorhandler(401)
def unauthorized(e):
    return "<h1>401</h1><p>Unauthorized</p>", 401

# Run the application
if __name__ == '__main__':
    app.run()
