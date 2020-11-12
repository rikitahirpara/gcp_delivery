# from flask import Flask
# from flask import jsonify
# from flask import redirect
import flask
import pandas as pd
import simplejson as json
#import wikipedia
from google.cloud import bigquery
app = flask.Flask(__name__)
client = bigquery.Client()

@app.route('/sql')
def sql():
    # """Return a friendly HTTP greeting."""
    # print("I am inside hello world")
    # return 'Hello World!!!!! How are you?'
    
    query_job = client.query(
        """
        SELECT * FROM `msds434-0.hurricanes.hurricanes` LIMIT 1000
        """
    )  # API request
    rows = query_job.result()  # Waits for query to finish

    for row in rows:
        print(row)
    
    return ""
    # return flask.redirect(
    #     flask.url_for(
    #         "results",
    #         project_id=query_job.project,
    #         job_id=query_job.job_id,
    #         location=query_job.location,
    #     )
    # )

@app.route('/')
def myform():
    return flask.render_template('form.html')

@app.route('/', methods=['POST'])
def myformpost():
    year = flask.request.form['year']
    status = flask.request.form['status'].upper()
    name = flask.request.form['name'].upper()
    wind = flask.request.form['wind']

    query_job = client.query(
        """
        SELECT sid,season,name,basin,nature,usa_eye,usa_status,wmo_wind,usa_record FROM `msds434-0.hurricanes.hurricanes` WHERE season='1990' AND name='FRAN' AND usa_status='WV' ORDER BY wmo_wind
        """
    )  # API request
    rows = query_job.result()  # Waits for query to finish
    # df=query_job.to_dataframe()
    # json_obj = df.to_json(orient='records')
    records = [dict(row) for row in query_job]
    json_obj = json.dumps(str(records),indent = 4, separators = (',', ': '))
    for row in rows:
        print(row.values)
    
    return json_obj
    #return flask.render_template('results.html')
    #return year+status+name+wind


@app.route('/results')
def results():
    project_id = flask.request.args.get("project_id")
    job_id = flask.request.args.get("job_id")
    location = flask.request.args.get("location")

    query_job = client.get_job(
        job_id,
        project=project_id,
        location=location,
    )

    try:
        results = query_job.result(timeout=30)
    except concurrent.futures.TimeoutError:
        return flask.render_template("timeout.html", job_id=query_job.job_id)
    print(results)
    return flask.render_template("query_result.html", results=results)

@app.route('/echo/<name>')
def echo(name):
    print("This was placed in the url: new-{name}")
    val = {"new-name": name}
    return jsonify(val)

@app.route('/html')
def html():
    return """
    <title>This is a Hello World Page </title>
    <p>Hello</p>
    <p><b>World</b></p>
    """
@app.route('/pandas')
def pandas_sugar():
    df = pd.read_csv("https://raw.githubusercontent.com/noahgift/sugar/master/data/education_sugar_cdc_2003.csv")
    return jsonify(df.to_dict())



# @app.route('/wikipedia/<company>')
# def wikipedia_route(company):
#     result = wikipedia.summary(company, sentences=10)
#     client = language.LanguageServiceClient()
#     document = types.Document(
#         content=result,
#         type=enums.Document.Type.PLAIN_TEXT
#     )
#     entities = client.analyze_entities(document).entities
#     return str(entities)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
