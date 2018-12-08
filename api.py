from flask import Flask, request, jsonify, render_template
import connections

app = Flask(__name__)


@app.route('/api/search', methods=['GET'])
def search():
    # TODO: Extend the API to allow from date_from, date_to (first fix it).
    source = request.args.get('source')
    destination = request.args.get('destination')
    date = request.args.get('date')
    if not source or not destination or not date:
        # TODO: Error response
        return 'Missing param, expects source, destination, and date.'
    results = connections.get_connections(source, destination, date)
    return jsonify(results)


@app.route('/search', methods=['GET'])
def search_view():
    source = request.args.get('source')
    destination = request.args.get('destination')
    date = request.args.get('date')
    if not source or not destination or not date:
        # TODO: Error response
        return 'Missing param, expects source, destination, and date.'
    journeys = connections.get_connections(source, destination, date)
    return render_template('results.html', journeys=journeys)
