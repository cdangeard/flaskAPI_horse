import flask
import pandas as pd
from pathlib import Path

path = str(Path(__file__).parent.absolute()) + '/'
app = flask.Flask(__name__) # create an app instance
app.config["DEBUG"] = True # enable debugging, auto-reload

def csv_to_json(filename, header=None):
    data = pd.read_csv(filename, header=header)
    return data.to_dict('records')

data = csv_to_json(path + './static/horse.csv', header=0)

@app.route('/api/v1/resources/horses/all', methods=['GET'])
def api_all():
    return flask.jsonify(data)

@app.route('/api/v1/resources/horse', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in flask.request.args:
        id = int(flask.request.args['id'])
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
    return flask.jsonify(results)

@app.route('/', methods=['GET'])
def home():
    return "<h1>API is working</h1><p>Flask is running.</p>"


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




app.run() # run the app

