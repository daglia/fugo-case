import json
from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import services.db as db_service
import services.api as api_service

app = Flask(__name__)


@app.route("/")
def index():
    return '''
      <h1>Fugo Case - themoviedb</h1>
      <h3>Database Operations:</h3>
      <ul>
        <a href="/dbdrop">Drop Database</a>
        <a href="/dbinit">Initialize Database</a>
        <a href="/dbinsert">Insert to Database</a>
      </ul>
      <h3>Queries:</h3>
      <ul>
        <a href="/toptenacting">Top 10 Acting</a>
        <a href="/toptenactingordered">Top 10 Acting with Order</a>
        <a href="/directorswork">Directors' Works</a>
        <a href="/topfivebycategories">Most Popular 5 People by Categories</a>
      </ul>
    '''


@app.route("/dbdrop")
def dp_drop():
    db_service.drop_db()

    return '''
      <h1>Fugo Case - themoviedb</h1>
      <p>Database drop is completed.</p>
      <a href="/">Go back</a>
    '''


@app.route("/dbinit")
def dp_init():
    db_service.init_db()

    return '''
      <h1>Fugo Case - themoviedb</h1>
      <p>Database initialization is completed.</p>
      <a href="/">Go back</a>
    '''


@app.route("/dbinsert")
def db_insert():
    series_data = api_service.get_series_data()
    db_service.insert_series_data(series_data)
    credits_data = api_service.get_credits_data(
        list(map(lambda x: x['id'], series_data)))
    db_service.insert_people_data(credits_data)

    return '''
      <p>Data insert is completed.</p>
      <a href="/">Go back</a>
    '''


@app.route("/toptenacting")
def top_ten_acting():
    result = db_service.get_top_ten_acting()
    return json.dumps(result)


@app.route("/toptenactingordered")
def top_ten_acting_ordered():
    result = db_service.get_top_ten_acting_ordered()
    return json.dumps(result)


@app.route("/directorswork")
def directors_work():
    result = db_service.get_directors_work()
    return json.dumps(result)


@app.route("/topfivebycategories")
def top_five_by_categories():
    result = db_service.get_top_five_by_categories()
    return json.dumps(result)


@app.route("/getfilterdata")
@cross_origin()
def get_filter_data():
    result = db_service.get_filter_data()
    return json.dumps(result)


@app.route("/getpeople")
@cross_origin()
def get_people():
    gender = request.args.get('gender')
    knownfor = request.args.get('knownfor')
    page = int(request.args.get('page'))
    limit = int(request.args.get('limit'))
    result = db_service.get_people(gender, knownfor, page, limit)
    return json.dumps(result)
