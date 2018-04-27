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


@app.route('/api/full_api', methods=['GET'])
def full_api():
    result_dict = query_db("SELECT * FROM customer")
    return jsonify({'data': result_dict})


@app.route('/api/econ_api', methods=['GET'])
def econ_api():
    connection = sqlite3.connect(DATABASE)
    query = 'SELECT customer.economic_stability, insurance_segment.value, \
            count(customer.economic_stability) as cnt \
            FROM customer \
            INNER JOIN insurance_segment \
            ON customer.insurance_segment_id = insurance_segment.id \
            GROUP BY customer.economic_stability, insurance_segment.value'
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
    max_y = data.groupby('economic_stability').sum()['cnt'].max()
    econ = list(data['economic_stability'].unique())
    return jsonify(dict(data=data_dict, max_y=max_y, econ=econ))


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

    for row in cursor.fetchall():
        data_dict[row[1]].append(row[0])

    data = []
    for key, value in data_dict.items():
        p75 = np.percentile(value, 75)
        p25 = np.percentile(value, 25)
        med = np.percentile(value, 50)
        iqr = p75 - p25
        max_num = p75 + 1.5*iqr if p75 + 1.5*iqr < max(value) else max(value)
        min_num = p25 - 1.5*iqr if p25 - 1.5*iqr > min(value) else min(value)
        data.append(dict(key=key, iqr=iqr, min=min_num, p25=p25, med=med,
                         p75=p75, max=max_num))

    min_y = min([i['min'] for i in data])
    max_y = max([i['max'] for i in data])

    return jsonify(dict(data=data, min_y=min_y, max_y=max_y))


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


if __name__ == '__main__':
    app.run(debug=True)
