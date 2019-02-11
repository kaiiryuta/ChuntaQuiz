# TO JSON PARSE
import json
# TO READ CSV
import csv
# TO RESOLVE HTTPREQUEST
import bottle
from bottle import route, run
from bottle import post, get, put, delete, request, response
# TO GET DATE
from datetime import datetime as dt
# sqlite3
import sqlite3
# SHA224
import hashlib

# --------------------------------------------------
# 定数
# --------------------------------------------------
# sqlite3ファイルパス
PATH_SQLITE3 = 'C:\\ChuntaQuiz\\chunta_quiz.db'

# --------------------------------------------------
# CORS対応
# ref https://stackoverflow.com/questions/17262170/bottle-py-enabling-cors-for-jquery-ajax-requests
# --------------------------------------------------
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors

app = bottle.app()

# --------------------------------------------------
# 認証
#
# CREATE TABLE users (id, pass);
# INSERT INTO users (id, pass) VALUES ('kaii-rt', 'kaii-rtpassword');
# --------------------------------------------------
@app.route('/auth', method=['OPTIONS', 'POST'])
@enable_cors
def auth():
    result = authontication(request.json)

    if result == True:
        response.status = 200
        return {}

    response.status = 403
    return {}

# --------------------------------------------------
# 一覧
#
# CREATE TABLE quiz (title, author, registday, question, answer);
# INSERT INTO quiz (title, author, registday, question, answer) VALUES ('タイトル', '作成者', '登録日', '問題', '答え');
# INSERT INTO quiz (title, author, registday, question, answer) VALUES ('タイトル2', '作成者2', '登録日2', '問題2', '答え2');
# --------------------------------------------------
@app.route('/list', method=['OPTIONS', 'POST'])
@enable_cors
def list():
    result = authontication(request.json)

    if result == False:
        response.status = 403
        return {}


    connection = sqlite3.connect(PATH_SQLITE3)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM quiz;')

    resultArray = cursor.fetchall()
    jsonObjectList = convertJsonObjectList(resultArray)

    connection.close()

    response.status = 200
    return json.dumps(jsonObjectList)

# --------------------------------------------------
# 検索
# --------------------------------------------------
@app.route('/selectByWord', method=['OPTIONS', 'POST'])
@enable_cors
def selectByWord():
    result = authontication(request.json)

    if result == False:
        response.status = 403
        return {}

    requestJson = request.json

    connection = sqlite3.connect(PATH_SQLITE3)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM quiz WHERE title like ? or question like ? or answer like ?;', ('%'+requestJson['keyword']+'%', '%'+requestJson['keyword']+'%', '%'+requestJson['keyword']+'%'))

    resultArray = cursor.fetchall()
    jsonObjectList = convertJsonObjectList(resultArray)

    connection.close()

    response.status = 200
    return json.dumps(jsonObjectList)

# --------------------------------------------------
# 認証
# --------------------------------------------------
def authontication(requestJson):
    connection = sqlite3.connect(PATH_SQLITE3)
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM users WHERE id = ? and pass = ?', (requestJson['id'], requestJson['password']))

    resultArray = cursor.fetchall()

    connection.close()

    if len(resultArray) == 0:
        return False

    return True

# --------------------------------------------------
# 辞書型を要素に持った配列に変換
# --------------------------------------------------
def convertJsonObjectList(resultArray):
    # リスト
    jsonObjectList = []

    for result in resultArray:
        # 辞書型
        jsonObject = {}

        jsonObject.setdefault('title', result[0])
        jsonObject.setdefault('author', result[1])
        jsonObject.setdefault('registday', result[2])
        jsonObject.setdefault('question', result[3])
        jsonObject.setdefault('answer', result[4])

        jsonObjectList.append(jsonObject)

    return jsonObjectList



# --------------------------------------------------
# webServer実行
# --------------------------------------------------
if __name__ == '__main__':
    # running on AWS
    # run (host='18.220.246.76', port=8080, debug=True, reloader=True)
    # running on local
    #run (host='localhost', port=8080, debug=True, reloader=True)
    run (host='ec2-18-223-22-197.us-east-2.compute.amazonaws.com', port=8080, debug=True, reloader=True)
