from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)


@app.route('/')
def index():
   print('Request for index page received')
   ip = request.remote_addr
   return render_template('index.html', **locals())

@app.route('/test')
def test():
   print('Request for test received')
   return render_template('index.html')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

@app.route('/api/test')
def api_test():
   print('Request for api test received')
   data = {'data1':1, 'data2':2, 'data3':3}
   return jsonify(data)


@app.route('/api/post', methods=['GET', 'POST'] )
def api_post():
   print('Request for api post received')
   req = request.get_json()
   return jsonify(req)



if __name__ == '__main__':
   app.run()