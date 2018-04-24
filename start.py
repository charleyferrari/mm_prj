import sys
import sqlite3

from flask import Flask, jsonify
from flask import render_template

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

if __name__ == '__main__':
    app.run()
