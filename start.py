import sys
import sqlite3

from flask import Flask, jsonify, send_from_directory
from flask import render_template

import pandas as pd
import numpy as np

app = Flask(__name__)

DATABASE = "./recruit.db"


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def query_db(query):

    result_dict = {}

    try:
        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()
        cursor.execute(query)
        result_dict = dictfetchall(cursor)

    except sqlite3.OperationalError as e:
        print("Db operation error", e)
        result_dict["error"] = str(e)
    except:  # noqa
        e = sys.exc_info()[0]
        print("An error occurred with the database", e)
        result_dict["error"] = str(e)
    else:
        cursor.close()
        connection.close()

    return result_dict


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/max_income', methods=['GET'])
def api_test():

    result_dict = query_db("select gender, max(income) as max_income from \
                           customer group by gender")
    # print(result_dict)

    return jsonify({'data': result_dict})


# API used for the stacked Bar Chart
# API returns json records of counts each insurance segment and Economic
# Stability scores. Each record is grouped into cumulative values and actual
# values. Cumulative values are used to draw the bars, while actual values are
# displayed in the tooltips
@app.route('/api/econ_api', methods=['GET'])
def econ_api():
    connection = sqlite3.connect(DATABASE)
    query = 'SELECT customer.economic_stability, insurance_segment.value, \
            count(customer.economic_stability) as cnt \
            FROM customer \
            INNER JOIN insurance_segment \
            ON customer.insurance_segment_id = insurance_segment.id \
            GROUP BY customer.economic_stability, insurance_segment.value'

    # Using Pandas for this because I wanted to pivot the data
    # Create one dict for Cumulative, one dict for pivot, then combine them.
    data = pd.read_sql(query, connection)
    data_pivot = data.pivot(index='economic_stability',
                            columns='value',
                            values='cnt')\
        .cumsum(axis=1).fillna(0).reset_index()
    data_pivot_vals = data.pivot(index='economic_stability',
                                 columns='value',
                                 values='cnt')\
        .fillna(0).reset_index()
    data_cum_dict = data_pivot.to_dict(orient='records')
    data_vals_dict = data_pivot_vals.to_dict(orient='records')
    data_dict = [dict(val=val, cum=cum)
                 for val, cum in zip(data_vals_dict, data_cum_dict)]

    # Since we're grouping traces, I found it convenient to pre-calculate the
    # max and min to get a full range. An array of economic stability scores
    # are also included for convenience.
    max_y = data.groupby('economic_stability').sum()['cnt'].max()
    econ = list(data['economic_stability'].unique())
    return jsonify(dict(data=data_dict, max_y=max_y, econ=econ))


# API used for the box plot. Everything is precalculated in flask, and the only
# values being passed on are the borders of the boxes. One record for each
# insurance segment.
@app.route('/api/box_api', methods=['GET'])
def box_api():
    connection = sqlite3.connect(DATABASE)

    data_dict = dict()

    insurance_segment = pd.read_sql('select * FROM insurance_segment',
                                    connection)

    for key in insurance_segment['value']:
        data_dict[key] = []

    query = 'SELECT customer.income, insurance_segment.value\
            FROM customer \
            INNER JOIN insurance_segment \
            ON customer.insurance_segment_id = insurance_segment.id'

    cursor = connection.cursor()
    cursor.execute(query)

    # Bring in the query in an initial dict structure
    for row in cursor.fetchall():
        data_dict[row[1]].append(row[0])

    # Calculate helpful values for building a boxplot, such as percentiles,
    # IQR, and whisker mins and maxes. Income is almost always right skewed, so
    # I decided to not include outliers in this visualization. In an
    # exploratory analysis, the distribution of income is more important than
    # visualizing outliers. Otherwise, I would have just added an array of
    # outliers to the data_dict.
    data = []
    for key, value in data_dict.items():
        p75 = np.percentile(value, 75)
        p25 = np.percentile(value, 25)
        med = np.percentile(value, 50)
        iqr = p75 - p25
        max_num = p75 + 1.5*iqr if p75 + 1.5*iqr < max(value) else max(value)
        min_num = p25 - 1.5*iqr if p25 - 1.5*iqr > min(value) else min(value)
        data.append(dict(key=str(key), iqr=float(iqr), min=float(min_num),
                         p25=float(p25), med=float(med), p75=float(p75),
                         max=float(max_num)))

    min_y = float(min([i['min'] for i in data]))
    max_y = float(max([i['max'] for i in data]))

    print(type(data[0]['key']))

    return jsonify(dict(data=data, min_y=min_y, max_y=max_y))


# routing for index.js
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


if __name__ == '__main__':
    app.run(debug=True)
