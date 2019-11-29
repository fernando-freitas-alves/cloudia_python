#!/usr/bin/env python3

from flask import Flask, jsonify, redirect, request, url_for
import mysql.connector
import time    


app = Flask(__name__)

db              = None
db_host         = "localhost"
db_user         = "root"
db_password     = "password"
db_database     = "cloudia_python"
db_users_table  = "users"
db_msgs_table   = "messages"
db_user_id_col  = 0
db_username_col = 1
db_msg_id_col   = 0
db_msg_user_col = 1
db_msg_col      = 2
db_msg_date_col = 3


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response             = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def isempty(x):
    return len(x) == 0


def db_connect():
    global db
    db     = mysql.connector.connect(host=db_host, user=db_user, password=db_password)
    cursor = db.cursor(buffered=True)
    cursor.execute("SHOW DATABASES")
    if not (db_database,) in cursor:
        cursor.execute("CREATE DATABASE cloudia_python")
    db     = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_database)
    cursor = db.cursor(buffered=True)

    cursor.execute("SHOW TABLES")
    if not (db_users_table,) in cursor:
        cursor.execute("CREATE TABLE " + db_users_table + " (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))")

    cursor.execute("SHOW TABLES")
    if not (db_msgs_table,) in cursor:
        cursor.execute("CREATE TABLE " + db_msgs_table + " (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, message VARCHAR(280), date TIMESTAMP NOT NULL)")


def db_insert_user(username):
    if db is None:
        db_connect()
    cursor = db.cursor(buffered=True)
    result = db_query_user_by_name(username)
    if isempty(result):
        sql = "INSERT INTO " + db_users_table + " (name) VALUES (%s)"
        val = (username,)
        cursor.execute(sql, val)
        db.commit()
        id     = cursor.lastrowid
        result = db_query_user_by_id(id)
    user = result[0]
    return user


def db_insert_msg(username, message):
    if db is None:
        db_connect()
    cursor  = db.cursor(buffered=True)
    user    = db_insert_user(username)
    user_id = user[db_user_id_col]
    date    = time.strftime('%Y-%m-%d %H:%M:%S')
    sql     = "INSERT INTO " + db_msgs_table + " (user_id, message, date) VALUES (%s,%s,%s)"
    val     = (user_id, message, date)
    cursor.execute(sql, val)
    db.commit()
    msg_id = cursor.lastrowid
    result = db_query_msg_by_id(msg_id)
    msg    = result[0]
    return msg


def db_query_all_from(table, suffix=""):
    if db is None:
        db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute("SELECT * FROM " + table + " " + suffix)
    result = cursor.fetchall()
    return result


def db_query_user_by_name(username):
    return db_query_all_from(db_users_table, "WHERE name='" + username + "'")


def db_query_user_by_id(id):
    return db_query_all_from(db_users_table, "WHERE id=" + str(id))


def db_query_msg_by_id(id):
    return db_query_all_from(db_msgs_table, "WHERE id=" + str(id))


def db_delete_from(table, suffix=""):
    if db is None:
        db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute("DELETE FROM " + table + " " + suffix)
    db.commit()


def db_delete_user_by_id(id):
    db_delete_from(db_users_table, "WHERE id=" + str(id))


def db_delete_user_by_name(username):
    db_delete_from(db_users_table, "WHERE name='" + username + "'")


def db_delete_msg_by_id(id):
    db_delete_from(db_msgs_table, "WHERE id=" + str(id))


def db_update(table, suffix):
    if db is None:
        db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute("UPDATE " + table + " " + suffix)
    db.commit()


def db_update_user_by_id(id, new_name):
    db_update(db_users_table, "SET name='" + new_name + "' WHERE id='" + str(id) + "'")
    result = db_query_user_by_id(id)
    return result


def db_update_user_by_name(username, new_name):
    db_update(db_users_table, "SET name='" + new_name + "' WHERE name='" + username + "'")
    result = db_query_user_by_name(new_name)
    return result


def db_update_msg_by_id(id, new_user_id, new_msg, new_date):
    db_update(db_msgs_table, "SET user_id='" + str(new_user_id) + "', message='" + new_msg + "', date='" + new_date + "' WHERE id='" + str(id) + "'")
    result = db_query_msg_by_id(id)
    return result


def db_clear_table(table):
    if db is None:
        db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute("TRUNCATE TABLE " + table)


def db_clear_tables():
    db_clear_users()
    db_clear_msgs()


def db_clear_users():
    db_clear_table(db_users_table)


def db_clear_msgs():
    db_clear_table(db_msgs_table)


def db_delete_table(table):
    if db is None:
        db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute("DROP TABLE " + table)


def db_delete_tables():
    db_delete_users()
    db_delete_msgs()


def db_delete_users():
    db_delete_table(db_users_table)


def db_delete_msgs():
    db_delete_table(db_msgs_table)


def get_username_from_data(data):
    if isempty(data):
        raise InvalidUsage("The 'user' key must be non-empty", status_code=422)
    if data.isdigit():
        user_id = int(data)
        result  = db_query_user_by_id(user_id)
        if isempty(result):
            raise InvalidUsage("User not found", status_code=422)
        user     = result[0]
        username = user[db_username_col]
    else:
        username = data
    return username


def users_dict(users_list):
    users_dict = {}
    for id, username in users_list:
        users_dict[id] = username
    return users_dict


def msgs_dict(msgs_list):
    msgs_dict = {}
    for msg_id, user_id, msg, date in msgs_list:
        result = db_query_user_by_id(user_id)
        if isempty(result):
            username = "*UNKNOWN*"
        else:
            user     = result[0]
            username = user[db_username_col]
        msgs_dict[msg_id]         = {}
        msgs_dict[msg_id]["user"] = username
        msgs_dict[msg_id]["msg"]  = msg
        msgs_dict[msg_id]["date"] = date
    return msgs_dict


@app.route('/api/users', methods=["GET"])
def get_users():
    result = db_query_all_from(db_users_table)
    return users_dict(result)


@app.route('/api/users/<int:id>', methods=["GET"])
def get_user_by_id(id):
    result = db_query_user_by_id(id)
    return users_dict(result)


@app.route('/api/users/<username>', methods=["GET"])
def get_user_by_name(username):
    result = db_query_user_by_name(username)
    return users_dict(result)


@app.route('/api/users', methods=["POST"])
def post_users():
    if request.args is not None and "name" in request.args:
        data = request.args
    else:
        json_data = request.get_json()
        if json_data is not None and "name" in json_data:
            data = json_data
        else:
            raise InvalidUsage("An user 'name' key must be provided", status_code=422)
    username = data["name"]
    if isempty(username):
        raise InvalidUsage("A non-empty username must be provided", status_code=422)
    user = db_insert_user(username)
    return users_dict([user])


@app.route('/api/users/<int:id>', methods=["DELETE"])
def delete_user_by_id(id):
    result = db_query_user_by_id(id)
    if isempty(result):
        raise InvalidUsage("User ID not found", status_code=422)
    db_delete_user_by_id(id)
    return "OK"


@app.route('/api/users/<username>', methods=["DELETE"])
def delete_user_by_name(username):
    result = db_query_user_by_name(username)
    if isempty(result):
        raise InvalidUsage("Username not found", status_code=422)
    db_delete_user_by_name(username)
    return "OK"


@app.route('/api/users/<int:id>', methods=["PUT"])
def put_user_by_id(id):
    result = db_query_user_by_id(id)
    if isempty(result):
        raise InvalidUsage("User ID not found", status_code=422)
    if request.args is not None and "name" in request.args:
        data = request.args
    else:
        json_data = request.get_json()
        if json_data is not None and "name" in json_data:
            data = json_data
        else:
            raise InvalidUsage("An user 'name' key must be provided", status_code=422)
    new_name = data["name"]
    if isempty(new_name):
        raise InvalidUsage("The new user 'name' key must be non-empty", status_code=422)
    result = db_query_user_by_name(new_name)
    if not isempty(result):
        raise InvalidUsage("Theres is already an user with the provided 'name' key", status_code=422)
    result  = db_update_user_by_id(id, new_name)
    return users_dict(result)


@app.route('/api/users/<username>', methods=["PUT"])
def put_user_by_name(username):
    result = db_query_user_by_name(username)
    if isempty(result):
        raise InvalidUsage("Username not found", status_code=422)
    if request.args is not None and "name" in request.args:
        data = request.args
    else:
        json_data = request.get_json()
        if json_data is not None and "name" in json_data:
            data = json_data
        else:
            raise InvalidUsage("An user 'name' key must be provided", status_code=422)
    new_name = data["name"]
    if isempty(new_name):
        raise InvalidUsage("The new user 'name' key must be non-empty", status_code=422)
    result = db_query_user_by_name(new_name)
    if not isempty(result):
        raise InvalidUsage("Theres is already an user with the provided 'name' key", status_code=422)
    result = db_update_user_by_name(username, new_name)
    return users_dict(result)


@app.route('/api/msgs', methods=["GET"])
def get_msgs():
    result = db_query_all_from(db_msgs_table)
    return msgs_dict(result)


@app.route('/api/msgs/<int:id>', methods=["GET"])
def get_msg_by_id(id):
    result = db_query_msg_by_id(id)
    return msgs_dict(result)


@app.route('/api/msgs', methods=["POST"])
def post_msgs():
    if request.args is not None and "user" in request.args and "msg" in request.args:
        data = request.args
    else:
        json_data = request.get_json()
        if json_data is not None and "user" in json_data and "msg" in json_data:
            data = json_data
        else:
            raise InvalidUsage("The keys 'user' and 'msg' must be provided", status_code=422)
    userdata = data["user"]
    username = get_username_from_data(userdata)
    msg      = data["msg"]
    result   = db_insert_msg(username, msg)
    return msgs_dict([result])


@app.route('/api/msgs/<int:id>', methods=["DELETE"])
def delete_msg_by_id(id):
    result = db_query_msg_by_id(id)
    if isempty(result):
        raise InvalidUsage("Message ID not found", status_code=422)
    db_delete_msg_by_id(id)
    return "OK"


@app.route('/api/msgs/<int:id>', methods=["PUT"])
def put_msg_by_id(id):
    result = db_query_msg_by_id(id)
    if isempty(result):
        raise InvalidUsage("Message ID not found", status_code=422)
    if request.args is not None and ("user" in request.args or "msg" in request.args):
        data = request.args
    else:
        json_data = request.get_json()
        if json_data is not None and ("user" in json_data or "msg" in json_data):
            data = json_data
        else:
            raise InvalidUsage("The keys 'user' and 'msg' must be provided", status_code=422)
    if "user" not in data:
        new_user_id = result[db_msg_user_col]
    else:
        new_user = data["user"]
        if isempty(new_user):
            raise InvalidUsage("The new user 'user' key must be non-empty", status_code=422)
        if new_user.isdigit():
            new_user_id = int(new_user)
            result      = db_query_user_by_id(new_user_id)
            if isempty(result):
                raise InvalidUsage("User not found", status_code=422)
        else:
            new_username = new_user
            result       = db_query_user_by_name(new_username)
            if isempty(result):
                raise InvalidUsage("User not found", status_code=422)
            user        = result[0]
            new_user_id = user[db_user_id_col]
    if "msg" not in data:
        new_msg = result[db_msg_col]
        if isempty(new_msg):
            raise InvalidUsage("The new message 'msg' key must be non-empty", status_code=422)
    else:
        new_msg = data["msg"]
    new_date = time.strftime('%Y-%m-%d %H:%M:%S')
    result   = db_update_msg_by_id(id, new_user_id, new_msg, new_date)
    return msgs_dict(result)


@app.route('/', methods=["GET"])
def get_index():
    return "BEE-BOP!"


@app.route('/', methods=["POST"])
def post_index():
    if request.args is not None and "user" in request.args and "msg" in request.args:
        data = request.args
    else:
        json_data = request.get_json()
        if json_data is not None and "user" in json_data and "msg" in json_data:
            data = json_data
        else:
            raise InvalidUsage("The keys 'user' and 'msg' must be provided", status_code=422)
    userdata = data["user"]
    username = get_username_from_data(userdata)
    msg      = data["msg"]
    db_insert_msg(username, msg)

    if msg is None or not msg.isdigit():
        return ""
    else:
        n = int(msg)
        if n % 15 == 0:
            return "FizzBuzz"
        if n % 3 == 0:
            return "Fizz"
        if n % 5 == 0:
            return "Buzz"
        else:
            return msg


@app.before_request
def clear_trailing():
    rp = request.path 
    if rp != '/' and rp.endswith('/'):
        return redirect(rp[:-1])


if __name__ == '__main__':
    # db_clear_tables()
    # db_delete_tables()
    app.run(debug=True)
    # app.run()
