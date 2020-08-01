from flask import Flask
from flask import request
from flaskext.mysql import MySQL
from flask import jsonify
from cryptography.fernet import Fernet
import hashlib

app = Flask(__name__)

# app.config['MYSQL_DATABASE_HOST'] = 'localhost:3306'
app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'workindia'

mysql = MySQL(app)
mysql.init_app(app)

# key has been already generated
key='emEL9ngzJJDaniuasNEpv-7LYnNxnlZwMDAPZroKbWo='.encode()
encryptFunc = Fernet(key)

@app.route("/")
def home():
    return "Hello!"

@app.route("/app/user",methods=["POST"])
def register():
    username = request.form['username']
    password = request.form['password']
    password = hashlib.md5(password.encode()).hexdigest()
    cursor = mysql.get_db().cursor()
    response = {}
    try:
        cursor.execute("INSERT INTO users (user_name,password) values (%s,%s)",(username,password))
        mysql.get_db().commit()
        cursor.close()
        response["status"] = "account created"
    except Exception as err:
        print(err)
        response["status"] = "duplicate username"
    return jsonify(response)
        

@app.route("/app/user/auth",methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    password = hashlib.md5(password.encode()).hexdigest()
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT user_id from users where user_name=%s and password=%s",(username,password))
    result = cursor.fetchall()
    response = {}
    if len(result)==0:
        response["status"]="failed"
    else:
        response["status"]="success"
        response["userId"]=result[0][0]
    cursor.close()
    return jsonify(response)

@app.route("/app/sites/list")
def listNotes():
    user_id = request.args["user"]
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT note from notes where user_id=%s",(user_id))
    result = cursor.fetchall()
    noteList=[]
    for row in result:
        for entry in row:
            noteList.append(encryptFunc.decrypt(entry.encode()))
    cursor.close()
    print(noteList)
    return jsonify(noteList)

@app.route("/app/sites",methods=["POST"])
def addNote():
    user_id = request.args["user"]
    note=request.form["note"].encode()
    note=encryptFunc.encrypt(note)
    print(note)
    cursor = mysql.get_db().cursor()
    cursor.execute("INSERT INTO notes (user_id,note) values (%s,%s)",(user_id,note))
    mysql.get_db().commit()
    cursor.close()
    return "success"