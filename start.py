import sys
import sqlite3

from flask import Flask, jsonify
from flask import render_template

import pandas as pd

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
    except:
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

    result_dict = query_db("select gender, max(income) as max_income from customer group by gender")
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
            INNER JOIN insurance_segment ON customer.insurance_segment_id = insurance_segment.id \
            GROUP BY customer.economic_stability, insurance_segment.value'
    data = pd.read_sql(query, connection)
    data_pivot = data.pivot(index='economic_stability', columns='value', values='cnt')\
        .cumsum(axis=1).fillna(0).reset_index()
    data_dict = data_pivot.to_dict(orient='records')
    max_y = data.groupby('economic_stability').sum()['cnt'].max()
    econ = list(data['economic_stability'].unique())
    return jsonify(dict(data=data_dict, max_y=max_y, econ=econ))


@app.route('/api/box_api', methods=['GET'])
def box_api():
    connection = sqlite3.connect(DATABASE)

    data_dict = dict()

    insurance_segment = pd.read_sql('select * FROM insurance_segment', connection)

    for key in insurance_segment['value']:
        data_dict[key] = []

    query = 'SELECT customer.income, insurance_segment.value\
            FROM customer \
            INNER JOIN insurance_segment ON customer.insurance_segment_id = insurance_segment.id'

    cursor = connection.cursor()
    cursor.execute(query)

    min_y = 1000000
    max_y = 0

    for row in cursor.fetchall():
        data_dict[row[1]].append(row[0])
        if row[0] < min_y:
            min_y = row[0]
        if row[0] > max_y:
            max_y = row[0]

    data = []
    for key, value in data_dict.items():
        data.append(dict(key=key, income=value))

    return jsonify(dict(data=data, min_y=min_y, max_y=max_y))


if __name__ == '__main__':
    app.run(debug=True)
