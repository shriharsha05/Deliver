"""
Deliver App
Developer : Shriharsha M [shriharsha05@computer.org]
"""

from flask import Flask, render_template, url_for, redirect, request, session, flash
from gevent.pywsgi import WSGIServer
from pymongo import MongoClient
import hashlib
import os

#flask config
app = Flask(__name__)
app.secret_key = os.environ['SECRET']

#db config
db_username = os.environ['DB_USER']
db_password = os.environ['DB_PASSWD']
client = MongoClient("mongodb+srv://"+db_username+":"+db_password+"/test?retryWrites=true&w=majority")
db = client["Deliver"]

@app.route('/', methods=['POST', 'GET'])
def index():
  if 'logged_in' in session and 'customer_logged_in' in session:
    return render_template('customer.html', username=session['user'])
  elif 'logged_in' in session:
    return redirect("/vendor")
  else:
    return redirect("/login")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'logged_in' in session and 'customer_logged_in':
        return redirect("/")
    elif 'logged_in' in session:
        return redirect("/vendor")
    if request.method=="GET":
        return render_template("login.html")
    else:
      try:
        data = db["users"].find({"username" : request.form["username"]})
        pswd_salt = os.environ['SALT']
        pswd = request.form["password"]
        digest = hashlib.sha512(str(pswd_salt+pswd+pswd_salt).encode('utf-8', 'strict'))
        if data[0]['password'] == digest.hexdigest():
            session['logged_in'] = True
            session['customer_logged_in'] = True
            session['user'] = request.form["username"]
            return redirect("/login")
        else:
            return render_template("login.html",error="Wrong Password")
      except:
        flash("Data not found")
        return redirect("/login")


@app.route('/logout', methods=['POST', 'GET'])
def logout():
  session.clear()
  return redirect("/login")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
  if request.method == "GET":
    return render_template("signup.html")
  else:

    pswd_salt = os.environ['SALT']
    pswd = request.form["password"]
    digest = hashlib.sha512(str(pswd_salt+pswd+pswd_salt).encode('utf-8', 'strict'))
    user = {"username" : request.form["username"],
            "password": digest.hexdigest(),
            "email": request.form["email"],
            "phone_no" : request.form["phone_no"],
            "news_paper": request.form["news_paper"],
            "area": request.form["area"],
            "vendor": request.form["vendor"],
            "city" : request.form["city"],
            "address" : request.form["address"] 
    }
    db["users"].insert(user)
    return redirect("/login")


@app.route('/vendor', methods=['POST', 'GET'])
def vendor():
  return render_template('vendor.html')


@app.route('/unsubscribers', methods=['POST', 'GET'])
def unsubscribers():
  return render_template('unsubscribers.html')


@app.route('/complaints', methods=['POST', 'GET'])
def complaints():
  return render_template('view_complaints.html')


@app.route('/info', methods=['POST', 'GET'])
def info():
  return render_template('delivery_person_details.html')


@app.route('/add', methods=['POST', 'GET'])
def add():
  return render_template('add_delivery_person.html')


@app.errorhandler(404)
def not_found(e):
  return render_template("404.html"), 404


@app.route('/sw.js', methods=['GET'])
def sw():
    return app.send_static_file('sw.js')


@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')


if __name__ == "__main__":
    # Development
    # app.run(host='0.0.0.0', port=8080, threaded=True, debug=True)

    #Production
    http_server = WSGIServer(('', 8080), app)
    http_server.serve_forever()
