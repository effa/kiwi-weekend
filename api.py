from flask import Flask, request, jsonify, render_template, make_response
import connections
from forms import SearchForm


app = Flask(__name__)


@app.route('/search', methods=['GET', 'POST'])
def search_app():
    form = SearchForm(csrf_enabled=False)
    if form.validate_on_submit():
        source = request.form.get('source')
        destination = request.form.get('destination')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')
        journeys = connections.get_connections_interval(
            source, destination, date_from, date_to)
        template = render_template('results.html', journeys=journeys)
        return make_response(template)
    return render_template('search.html', form=form)


#@app.route('/search', methods=['GET'])
#def search_view():
#    try:
#        search_args = get_search_request_args()
#    except ValueError as exc:
#        return str(exc)  # TODO: Error response
#    journeys = connections.get_connections_interval(*search_args)
#    return render_template('results.html', journeys=journeys)


@app.route('/api/search', methods=['GET'])
def search():
    try:
        search_args = get_search_request_args()
    except ValueError as exc:
        return str(exc)  # TODO: Error response
    journeys = connections.get_connections_interval(*search_args)
    return jsonify(journeys)


def get_search_request_args():
    source = request.args.get('source')
    destination = request.args.get('destination')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    if not source or not destination or not date_from or not date_to:
        raise ValueError('Missing param. Expects source, destination, date_from, date_to.')
    return source, destination, date_from, date_to
