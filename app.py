"""
Deliver App
Developer : Shriharsha M [shriharsha05@computer.org]
"""

from flask import Flask, render_template, url_for, redirect, request, session
from gevent.pywsgi import WSGIServer
from pymongo import MongoClient
import hashlib,os,datetime,json
from flask_compress import Compress

#flask config
app = Flask(__name__)
app.secret_key = os.environ['SECRET']
Compress(app)

#db config
db_username = os.environ['DB_USER']
db_password = os.environ['DB_PASSWD']
client = MongoClient("mongodb+srv://"+db_username+":"+db_password+"/test?retryWrites=true&w=majority")
db = client["Deliver"]

@app.route('/', methods=['POST', 'GET'])
def index():
  if 'customer_logged_in' in session:
    return redirect("/customer")
  elif 'vendor_logged_in' in session:
    return redirect("/vendor")
  else:
    return redirect("/login")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'vendor_logged_in' in session or 'customer_logged_in' in session:
        return redirect("/")
    if request.method=="GET":
        return render_template("login.html")
    else:
      error = None
      try:
        #vendor demo login
        if request.form["username"] == "vendor" and request.form["password"] == os.environ['VENDOR']:
          session['vendor_logged_in'] = True
          return redirect("/")
        #user authentication
        data = db["users"].find({"username" : request.form["username"]})
        pswd_salt = os.environ['SALT']
        pswd = request.form["password"]
        digest = hashlib.sha512(str(pswd_salt+pswd+pswd_salt).encode('utf-8', 'strict'))
        if data[0]['password'] == digest.hexdigest():
            session['logged_in'] = True
            session['customer_logged_in'] = True
            session['user'] = request.form["username"]
            return redirect("/")
        else:
            error = "Invalid credentials!"
            return render_template("login.html",error=error)
      except:
        error = "Unregistered user. Please Sign Up before logging in!"
        return render_template("login.html", error=error)


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
    #insert record 
    db["users"].insert(user)
    return redirect("/login")


@app.route('/customer', methods=['POST', 'GET'])
def customer():
  if 'customer_logged_in' not in session:
        return redirect("/")
  data = db["users"].find({"username": session['user']})
  if request.method == "GET":
        return render_template('customer.html', data=data[0])
  else:
        try:  
              unsubscribe = {"username": data[0]['username'],
              "from_date": request.form['from_date'],
              "to_date": request.form['to_date'],
              "news_paper": data[0]['news_paper'],
              "area": data[0]['area'],
              "phone_no": data[0]['phone_no'],
              "resolved" : "0",
              "req_date" :datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
              }
              #insert unsubscription record
              db["unsubscribes"].insert(unsubscribe)
              #success
              return "1"
        except:
              try:
                    complaint = {"username": data[0]['username'],
                    "er_date": request.form['er_date'],
                    "news_paper": data[0]['news_paper'],
                    "area": data[0]['area'],
                    "phone_no": data[0]['phone_no'],
                    "resolved" : "0",
                    "complained_date" :datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
                    }
                    #insert unsubscription record
                    db["complaints"].insert(complaint)
                    #success
                    return "1"
              except:
                    return "2"
              return "2"

@app.route('/vendor', methods=['POST', 'GET'])
def vendor():
  if 'vendor_logged_in' not in session:
        return redirect("/")
  return render_template('vendor.html')


@app.route('/unsubscribers', methods=['POST', 'GET'])
def unsubscribers():
  if 'vendor_logged_in' not in session:
        return redirect("/")
  data = db["unsubscribes"].find().sort([('$natural', -1)])
  return render_template('unsubscribers.html', data=data)


@app.route('/complaints', methods=['POST', 'GET'])
def complaints():
  if 'vendor_logged_in' not in session:
        return redirect("/")
  data = db["complaints"].find().sort([('$natural', -1)])
  return render_template('view_complaints.html', data=data)


@app.route('/info', methods=['POST', 'GET'])
def info():
  if 'vendor_logged_in' not in session:
        return redirect("/")
  data = db["workers"].find().sort([('$natural', -1)])
  return render_template('delivery_person_details.html', data=data)


def addWorker(worker):
    db["workers"].insert(worker)


@app.route('/add', methods=['POST', 'GET'])
def add():
  if 'vendor_logged_in' not in session:
        return redirect("/")
  if request.method == "GET":
        return render_template('add_delivery_person.html')
  else:
        try:
          addWorker(json.loads(request.form["worker"]))
          return "1"
        except:
          return "2"
        

# @app.route('/test', methods=['POST', 'GET'])
# def test():
#   return render_template("test.html")


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
