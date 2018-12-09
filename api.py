from flask import Flask, request, jsonify, render_template
import connections

app = Flask(__name__)


@app.route('/api/search', methods=['GET'])
def search():
    try:
        search_args = get_search_request_args()
    except ValueError as exc:
        return str(exc)  # TODO: Error response
    journeys = connections.get_connections_interval(*search_args)
    return jsonify(journeys)


@app.route('/search', methods=['GET'])
def search_view():
    try:
        search_args = get_search_request_args()
    except ValueError as exc:
        return str(exc)  # TODO: Error response
    journeys = connections.get_connections_interval(*search_args)
    return render_template('results.html', journeys=journeys)


def get_search_request_args():
    source = request.args.get('source')
    destination = request.args.get('destination')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    if not source or not destination or not date_from or not date_to:
        raise ValueError('Missing param. Expects source, destination, date_from, date_to.')
    return source, destination, date_from, date_to
