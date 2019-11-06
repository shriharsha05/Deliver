"""
Deliver App
Developer : Shriharsha M [shriharsha05@computer.org]
"""

from flask import Flask, render_template, url_for, redirect, request, session, flash
from gevent.pywsgi import WSGIServer


#flask config
app = Flask(__name__)
app.secret_key = 'SECRET_KEY'


@app.route('/', methods=['POST', 'GET'])
def index():
  return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
  return render_template('login.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
  #session.clear()
  return redirect("/login")


@app.route('/customer', methods=['POST', 'GET'])
def customer():
  return render_template('customer.html')


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
