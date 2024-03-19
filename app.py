from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import jwt
import hashlib
import datetime
app = Flask(__name__)

# secret key
secret_key = 'jungbae'

# mongo db
client = MongoClient('localhost', 27017)
db = client.bdground

# CONTANTS
SURVICE_TITLE = "BAEDALGROUNDS"
LOGO_URL = './images/logo.png'

# 메인 페이지
@app.route('/')
def deliveryBoardPage():
  return render_template('main.html', service_title=SURVICE_TITLE, image =LOGO_URL)

# 로그인
@app.route('/login')
def loginPage():
  return render_template('login.html', service_title=SURVICE_TITLE, image =LOGO_URL)

@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    
    print(id_receive)
    
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result :  ## if result:
  
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'})

@app.route('/signIn')
def signInPage():
  return render_template('signIn.html', service_title=SURVICE_TITLE, image=LOGO_URL)

@app.route('/api/signIn',methods = ['POST'])
def api_signIn():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']
    
    print(id_receive, pw_receive, name_receive)
    #existing = db.bdground.find_one({'id':id_receive})
    # if existing:
    #   print('중복되었습니다,')
    #   return jsonify({'result': 'fail', 'msg': '아이디가 중복되었습니다.'})
      
  
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'name': name_receive})

    return jsonify({'result': 'success'})

#중복확인 api
@app.route('/api/signIn/confirm',methods = ['POST'])
def api_confirm():
    id_receive = request.form['id_give']
    result = db.user.find_one({'id': id_receive})
    if result:
      return jsonify({'result': 'fail', 'msg': '아이디가 중복되었습니다.'})
    else:
      return jsonify({'result': 'success'})
      
    
    
  



#main
@app.route('/api/isAuth', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, secret_key, algorithms=['HS256'])
        userinfo = db.user.find_one({'id': payload['id']})
        return jsonify({'result': 'success', 'name': userinfo['name']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

if __name__ == '__main__':  
  app.run('0.0.0.0',port=5001,debug=True)